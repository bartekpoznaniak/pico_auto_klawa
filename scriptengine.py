import time

last_x = 0
last_y = 0
VERSION = "1.1"

def run(path, h, show=lambda s: None):
    with open(path) as f:
        lines = f.read().split("\n")

    for n, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        cmd, _, arg = line.partition(" ")
        cmd = cmd.upper()
        show("%s:%d %s" % (path.split("/")[-1], n, cmd))

        try:
            if cmd == "WAIT":
                time.sleep(float(arg))
            elif cmd == "MOVE":
                x, y = arg.split()
                x = int(x)
                y = int(y)
                h["move"](x, y)
                last_x = x
                last_y = y
            elif cmd == "CLICK":
                h["click"]()
            elif cmd == "DOWN":
                h["down"]()
            elif cmd == "UP":
                h["up"]()
            elif cmd == "DRAG":
                p = arg.split()
                if len(p) not in (4, 5):
                    raise ValueError("DRAG x1 y1 x2 y2 [kroki]")
                steps = int(p[4]) if len(p) == 5 else 20
                h["drag"](int(p[0]), int(p[1]), int(p[2]), int(p[3]), steps)
            elif cmd == "TYPE":
                h["type"](arg)
            elif cmd == "KEY":
                h["keys"]([arg.upper()])
            elif cmd == "HOTKEY":
                h["keys"](arg.upper().split())
            else:
                show("? " + line)
                return False
        except Exception as e:
            show("ERR %d" % n)
            print("line", n, e)
            return False

    return True