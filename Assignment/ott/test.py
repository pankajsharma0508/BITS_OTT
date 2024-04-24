from queue import Queue


queue = Queue()

# Enqueue elements
queue.put(1)
queue.put(2)
queue.put(3)


while not queue.empty():
    print("Dequeued:", queue.get())
