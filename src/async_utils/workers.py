import asyncio
from asyncio import locks


class WorkersManager:
    def __init__(self, queue: asyncio.Queue, max_workers:int) -> None:
        self._queue = queue
        self._max_workers = max_workers
        self._semaphore = asyncio.Semaphore(max_workers) # for managing number of workers
        self._finished = locks.Event() # flag to check if all the tasks are finished or not
        self._can_process = locks.Event() # to check if we can process any more tasks
        self._can_process.set() # at initialization we can definitely process more tasks
        self._finished.set() # at initialization all the tasks are finished
        self._ongoing_tasks_count = 0
        self._lock = locks.Lock() # lock to manage flags and attributes

    async def _assign_worker(self, function, *function_args, **function_kwargs):
        async with self._semaphore:
            await function(*function_args,**function_kwargs)
            async with self._lock:
                self._queue.task_done()
                self._ongoing_tasks_count -= 1
                if self._ongoing_tasks_count == 0:
                    self._finished.set()
                if self._ongoing_tasks_count < self._max_workers:
                    self._can_process.set()

    
    async def process_queue(self) -> None:
        while not self._queue.empty() or not self._finished.is_set():
            await self._can_process.wait() # wait until we can process more tasks
            if not self._queue.empty():
                function, *function_args = await self._queue.get()
                async with self._lock:
                    self._finished.clear()
                    asyncio.create_task(
                        self._assign_worker(function, *function_args)
                    )
                    self._ongoing_tasks_count += 1

                    # if the ongoing tasks exceed max allowed tasks, clear _can_process flag
                    if self._ongoing_tasks_count>=self._max_workers:
                        self._can_process.clear()
            elif not self._finished.is_set(): # if queue is empty, wait for current workers to add more data into queue
                await asyncio.sleep(2)
        
        await self._finished.wait() # wait for all tasks to finish