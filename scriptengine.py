import time


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
                h["move"](int(x), int(y))
            elif cmd == "CLICK":
                h["click"]()
            elif cmd == "DOWN":
                h["down"]()
            elif cmd == "UP":
                h["up"]()
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