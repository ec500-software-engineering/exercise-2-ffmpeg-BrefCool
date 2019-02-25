import time
import npyscreen
from encode import encode_c480, encode_c720
from multiprocessing import Process, Queue, Manager

PROCESS_NUM = 10

def encode(task_q, messages, id):
	while True:
		messages[id] = 'waiting task'
		filename = task_q.get()
		parsed = filename.split('.')
		fout_480p = "".join(parsed[:-1]) + "_480p." + parsed[-1]
		fout_720p = "".join(parsed[:-1]) + "_720p." + parsed[-1]
		messages[id] = 'recv file to encode {}'.format(filename)
		time.sleep(0.5)
		messages[id] = 'converting file({}) to 480p...'.format(filename)
		succeed, output = encode_c480(filename, fout_480p)
		if not succeed:
			messages[id] = 'convert 480p failed.'
			time.sleep(5)
			continue
		time.sleep(1)
		messages[id] = 'converting file({}) to 720p...'.format(filename)
		succeed, output = encode_c720(filename, fout_720p)
		if not succeed:
			messages[id] = 'convert 720p failed.'
			time.sleep(5)
			continue
		messages[id] = 'Succeess'
		time.sleep(1)

class VideoEncoderApp(npyscreen.NPSAppManaged):
	def onStart(self):
		self.keypress_timeout_default = 1
		self.manager = Manager()
		self.messages = self.manager.dict()
		self.task_q = Queue()
		self.msg_q = Queue()
		self.pool = []
		self.addForm("MAIN", MainForm, name="Video Encoder")
		

		for i in range(PROCESS_NUM):
			p = Process(target=encode, args=(self.task_q, self.messages, i))
			p.start()
			self.pool.append(p)

	def onCleanExit(self):
		npyscreen.notify_wait("Goodbye!")

		# terminate all the processes
		for process in self.pool:
			process.terminate()
			time.sleep(0.1)

class MainForm(npyscreen.ActionForm):
	def create(self):
		self.keypress_timeout_default = 1
		self.process_fields = []
		self.fn = self.add(npyscreen.TitleFilenameCombo, name="filename: ")
		self.status = self.add(npyscreen.MultiLineEdit, value="Welcome! Please choose mp4 or mov file to encode\n", max_height=10, rely=9, editable=False)
		self.stdout = None
		for i in range(PROCESS_NUM):
			process_name = "process {}:".format(i)
			self.process_fields.append(self.add(npyscreen.TitleText, name=process_name, value="initializing", editable=False))

	def while_waiting(self):
		for i in range(PROCESS_NUM):
			if i in self.parentApp.messages:
				self.process_fields[i].value = self.parentApp.messages[i]
				self.process_fields[i].display()
			if self.stdout is not None:
				self.status.value += self.stdout
				self.stdout = None
				self.status.display()

	def on_cancel(self):
		self.parentApp.setNextForm(None)

	def on_ok(self):
		filename = self.fn.value
		parsed = filename.split('.')
		if len(parsed) > 1:
			suffix = parsed[-1]
			if suffix == 'mp4'or suffix == 'mov':
				self.parentApp.task_q.put(filename)
				self.stdout = "add file({}) to task queue(current size:{})\n".format(filename, self.parentApp.task_q.qsize())
			else:
				self.stdout = "invalid filename({}). mp4 or mov file required.\n".format(filename)
		else:
			self.stdout = "invalid filename({}). mp4 or mov file required.\n".format(filename)


if __name__ == "__main__":
	app = VideoEncoderApp()
	app.run()