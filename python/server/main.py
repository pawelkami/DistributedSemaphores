import traceback
import server

if __name__ == "__main__":

    try:
        server.run()
    except:
        print(traceback.format_exc())

