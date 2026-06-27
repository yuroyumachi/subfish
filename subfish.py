import sys
import signal

signal.signal(signal.SIGINT, lambda *_: sys.exit(signal.SIGINT))

AVAILABLE_OPERATOR = {
	"i", "d", "s", "o",
	"h", "t", "c", "z",
	"m", "p", "k", "n"
}

class Subfish:
	def __init__(self)-> None:
		self._acc: list[int]= [0, 0, 0]
		self._current_acc: int = 0

		self._source: str = ""
		self._src_ptr: int = 0
		self._mark_ptr: int = 0

		self.reset_getchar()

	def switch_accumulator(self)-> None:
		"""
		切换累加器
		轮切 self._acc 中的各个累加器
		"""
		self._current_acc = (self._current_acc + 1) % 3

	def source_pointer_advance(self)-> None:
		"""
		将源 代码指针递进
		"""
		if self._src_ptr < len(self._source):
			self._src_ptr += 1

	def current_source_character(self)-> str:
		"""
		返回当前源 代码指针所指向的字符
		"""
		if self._src_ptr < len(self._source):
			return self._source[self._src_ptr]
		return ""

	def skip_source_character(self, amount: int)-> None:
		"""
		将源代码跳过 amount 个字符
		"""
		for _ in range(amount):
			self.source_pointer_advance()
			if not self.current_source_character():
				break

	def reset_getchar(self)-> None:
		"""
		重置用户输入
		"""
		self._input: str = ""
		self._position: int = 0

	def getchar(self)-> str:
		"""
		返回一个字符,
		如果没有字符或者读取到了用户输入的尽头,
		则要求用户输入后, 再返回一个字符
		用户的输入的末尾有换行符
		"""
		if self._position >= len(self._input):
			self.reset_getchar()
			self._input = input() + "\n"
			return self.getchar()
		self._position += 1
		return self._input[self._position - 1]

	def feed(self, source: str)-> None:
		"""
		将更多 code 喂进来
		"""
		self._source += source
		self.exec()

	def exec(self)-> None:
		while self._src_ptr < len(self._source):
			ch = self.current_source_character()

			if ch == "i":
				"""
				递增当前累加器
				"""
				self._acc[self._current_acc] += 1
			
			elif ch == "d":
				"""
				递减当前累加器
				"""
				self._acc[self._current_acc] -= 1
			
			elif ch == "s":
				"""
				将当前累加器取平方
				"""
				self._acc[self._current_acc] *= self._acc[self._current_acc]
			
			elif ch == "o":
				"""
				输出当前累加器的数值
				"""
				print(self._acc[self._current_acc])
			
			elif ch == "h":
				"""
				halt
				"""
				sys.exit(0)
			
			elif ch == "t":
				"""
				切换累加器(一共三个)
				"""
				self.switch_accumulator()
			
			elif ch == "c":
				"""
				将当前累加器的数值作为 utf8 字符输出
				"""
				print(chr(self._acc[self._current_acc]), end="")
			
			elif ch == "z":
				"""
				如果当前累加器为 0
				那么跳过跳过往后的 10 个字符
				或者说是包括 z 的 11 个字符, 循环尾部
				"""
				self.source_pointer_advance()
				if self._acc[self._current_acc] == 0:
					self.skip_source_character(10)
				continue
			
			elif ch == "m":
				"""
				标记当前源代码指针
				"""
				self._mark_ptr = self._src_ptr

			elif ch == "p":
				"""
				将源代码指针跳转到标记的位置, 默认为 0
				"""
				self._src_ptr = self._mark_ptr
				continue
			
			elif ch == "k":
				"""
				从用户输入读取一个字符,
				并将当前累加器的值修改为该字符的值
				如果输入为空, 则什么都不做
				"""
				if ch := self.getchar():
					self._acc[self._current_acc] = ord(ch)

			elif ch == "n":
				"""
				什么也不做,
				通常用作 z 跳过时的占位符
				"""

			self.source_pointer_advance()

def preprocess(string: str)-> str:
	"""
	去除操作符以外的字符
	去除注释(以 # 开头, 以换行符结尾)
	"""
	skip_character: bool = False
	buffer = ""

	for ch in string:
		if skip_character:
			if ch == "\n":
				skip_character = False
			continue
		elif ch == "#":
			skip_character = True
		elif ch in AVAILABLE_OPERATOR:
			buffer += ch
		else:
			del ch

	return buffer

def main()-> None:
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("file", help="要执行的文件")
	parser.add_argument("-P", "--preprocess-only", action="store_true", help="输出预处理后的代码并退出")

	if len(sys.argv[1:]) == 0:
		parser.print_help()

	args = parser.parse_args(sys.argv[1:])

	try:
		with open(args.file, mode="rt", encoding="utf8") as file:
			source = file.read()
	except FileNotFoundError:
		print(f"subfish: file {args.file} not found", file=sys.stderr)
		sys.exit(1)

	if args.preprocess_only:
		print(preprocess(source))
		sys.exit(0)

	env = Subfish()
	env.feed(preprocess(source))

if __name__ == '__main__':
	main()
