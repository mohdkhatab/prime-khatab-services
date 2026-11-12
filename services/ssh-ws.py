#!/usr/bin/env python3
import asyncio

DROPBEAR_HOST = "127.0.0.1"
DROPBEAR_PORT = 109

VMESS_PORT = 10086
TROJAN_PORT = 10087

RESPONSE_101 = b"HTTP/1.1 101 Prime Khatab Services Connected\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nServer: Prime-Khatab-Services\r\n\r\n"
RESPONSE_200 = b"HTTP/1.1 200 Prime Khatab Services Connected\r\n\r\n"

async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            data = await reader.read(8192)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except Exception:
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def handle_client(client_reader, client_writer):
    target_writer = None
    try:
        header = await client_reader.read(4096)
        if not header:
            client_writer.close()
            return
        
        header_str = header.decode("latin1", errors="ignore")
        first_line = header_str.split("\r\n")[0] if "\r\n" in header_str else header_str

        # Check destination based on request line / path
        if "/vmess" in first_line:
            target_reader, target_writer = await asyncio.open_connection("127.0.0.1", VMESS_PORT)
            target_writer.write(header)
            await target_writer.drain()
        elif "/trojan" in first_line:
            target_reader, target_writer = await asyncio.open_connection("127.0.0.1", TROJAN_PORT)
            target_writer.write(header)
            await target_writer.drain()
        else:
            # Dropbear SSH Tunnel
            target_reader, target_writer = await asyncio.open_connection(DROPBEAR_HOST, DROPBEAR_PORT)
            if header.startswith(b"GET") or "upgrade: websocket" in header_str.lower():
                client_writer.write(RESPONSE_101)
                await client_writer.drain()
            elif header.startswith(b"CONNECT"):
                client_writer.write(RESPONSE_200)
                await client_writer.drain()
            else:
                target_writer.write(header)
                await target_writer.drain()

        await asyncio.gather(
            pipe(client_reader, target_writer),
            pipe(target_reader, client_writer)
        )
    except Exception:
        pass
    finally:
        try:
            client_writer.close()
            await client_writer.wait_closed()
        except Exception:
            pass
        if target_writer:
            try:
                target_writer.close()
                await target_writer.wait_closed()
            except Exception:
                pass

async def main():
    ports = [80, 8080, 8880]
    servers = []
    for p in ports:
        try:
            srv = await asyncio.start_server(handle_client, "0.0.0.0", p)
            servers.append(srv)
        except Exception as e:
            print(f"Warning: Failed to bind port {p}: {e}")
    
    await asyncio.gather(*(s.serve_forever() for s in servers))

if __name__ == "__main__":
    asyncio.run(main())
