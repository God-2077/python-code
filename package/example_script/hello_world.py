import datetime
import time
import sys
if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        # test 是否包含 --test
        if "--test" in sys.argv or "-t" in sys.argv or "test" in sys.argv:
            # print("Msg: Ciallo～(∠・ω< )⌒☆")
            print("Code: 0x0d000721")
            sys.exit(0)
    print("Message: Hello, World!")
    print("当前时间:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("当前时间戳:", time.time())
    print("__file__:", __file__)
