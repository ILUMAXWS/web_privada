import net from "node:net";
import tls from "node:tls";

const chunks = [];
for await (const chunk of process.stdin) {
  chunks.push(chunk);
}

const options = JSON.parse(Buffer.concat(chunks).toString("utf8"));

function b64(value) {
  return Buffer.from(value, "utf8").toString("base64");
}

function foldBase64(value) {
  return b64(value).match(/.{1,76}/g).join("\r\n");
}

function encodeHeader(value) {
  return `=?UTF-8?B?${b64(value)}?=`;
}

function createSocket() {
  return new Promise((resolve, reject) => {
    const socketOptions = {
      host: options.host,
      port: Number(options.port),
      servername: options.host,
      rejectUnauthorized: options.tls_verify !== false,
      timeout: 20000,
    };
    const socket = options.use_ssl ? tls.connect(socketOptions) : net.connect(socketOptions);
    socket.setEncoding("utf8");
    socket.once("connect", () => resolve(socket));
    socket.once("secureConnect", () => resolve(socket));
    socket.once("timeout", () => {
      socket.destroy(new Error("SMTP connection timed out"));
    });
    socket.once("error", reject);
  });
}

function readReply(socket) {
  return new Promise((resolve, reject) => {
    let buffer = "";

    const cleanup = () => {
      socket.off("data", onData);
      socket.off("error", onError);
    };

    const onError = (error) => {
      cleanup();
      reject(error);
    };

    const onData = (chunk) => {
      buffer += chunk;
      const lines = buffer.split(/\r?\n/).filter(Boolean);
      if (!lines.length) return;
      const last = lines[lines.length - 1];
      if (/^\d{3} /.test(last)) {
        cleanup();
        resolve({ code: Number(last.slice(0, 3)), text: buffer });
      }
    };

    socket.on("data", onData);
    socket.on("error", onError);
  });
}

async function command(socket, value, expected) {
  socket.write(`${value}\r\n`);
  const reply = await readReply(socket);
  const expectedCodes = Array.isArray(expected) ? expected : [expected];
  if (!expectedCodes.includes(reply.code)) {
    throw new Error(`SMTP command failed (${value}): ${reply.text}`);
  }
  return reply;
}

function address(email) {
  return `<${email}>`;
}

function messageData() {
  const headers = [
    `Subject: ${encodeHeader(options.subject)}`,
    `From: ${options.from_name ? `"${options.from_name}" ` : ""}${address(options.from_email)}`,
    `To: ${address(options.to_email)}`,
    "MIME-Version: 1.0",
    "Content-Type: text/plain; charset=UTF-8",
    "Content-Transfer-Encoding: base64",
  ];
  const body = foldBase64(options.text_body);
  return `${headers.join("\r\n")}\r\n\r\n${body}`;
}

let socket = await createSocket();
let reply = await readReply(socket);
if (reply.code !== 220) throw new Error(reply.text);

await command(socket, "EHLO localhost", 250);

if (options.use_tls && !options.use_ssl) {
  await command(socket, "STARTTLS", 220);
  socket = tls.connect({ socket, servername: options.host, rejectUnauthorized: options.tls_verify !== false });
  socket.setEncoding("utf8");
  await new Promise((resolve, reject) => {
    socket.once("secureConnect", resolve);
    socket.once("error", reject);
  });
  await command(socket, "EHLO localhost", 250);
}

if (options.user) {
  await command(socket, "AUTH LOGIN", 334);
  await command(socket, b64(options.user), 334);
  await command(socket, b64(options.password ?? ""), 235);
}

await command(socket, `MAIL FROM:${address(options.from_email)}`, 250);
await command(socket, `RCPT TO:${address(options.to_email)}`, [250, 251]);
await command(socket, "DATA", 354);

const data = messageData()
  .split(/\r?\n/)
  .map((line) => (line.startsWith(".") ? `.${line}` : line))
  .join("\r\n");

socket.write(`${data}\r\n.\r\n`);
reply = await readReply(socket);
if (reply.code !== 250) throw new Error(reply.text);

await command(socket, "QUIT", 221);
socket.end();
