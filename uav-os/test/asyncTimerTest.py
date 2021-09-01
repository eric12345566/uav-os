from helper.AsyncTimer import AsyncTimer

if __name__ == "__main__":
    timer = AsyncTimer(5)
    timer.startTimer()

    while timer.isTimesUp():
        print("async")

    print("time's up")
