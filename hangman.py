import random
from .images import hangmen
from halibot import HalModule

class Game():
	class Guess():
		success  = 0
		failure  = 1
		gameover = 2
		won      = 3
		already  = 4

	def __init__(self, wordlist, maxGuesses):
		self.word       = random.choice(wordlist).lower()
		self.got        = '-' * len(self.word)
		self.guessed    = ''
		self.maxGuesses = maxGuesses
		self.failures   = 0

	def guess(self, char):

		char = char.lower()
		
		if self.failures == self.maxGuesses:
			# Game over already
			result = Game.Guess.gameover
		elif self.got.count('-') == 0:
			result = Game.Guess.won
		elif char in self.guessed:
			# Already guessed
			result = Game.Guess.already
		else:
			result = Game.Guess.failure
			self.guessed += char

			# Did we get anything?
			for i in range(0, len(self.word)):
				if char == self.word[i]:
					self.got = self.got[:i] + self.word[i] + self.got[i+1:]
					result = Game.Guess.success

			if result == Game.Guess.failure:
				self.failures += 1	
				if self.failures == self.maxGuesses:
					result = Game.Guess.gameover
			else:
				if self.got.count('-') == 0:
					result = Game.Guess.won

		return result

	def board(self):
		percent = self.failures / self.maxGuesses
		index = int(percent * (len(hangmen)-1) + 0.5)
		return hangmen[index] + self.got + '\n'
		

class Hangman(HalModule):

	options = {
		'wordlist': {
			'type'    : 'string',
			'prompt'  : 'Word list file',
			'default' : 'words.txt',
		},
		'max-guesses': {
			'type'    : 'int',
			'prompt'  : 'Maximum guesses',
			'default' : '6',
		},
	}

	def init(self):
		self.game = None

		try:
			with open(self.config['wordlist']) as f:
				self.wordlist = [w.strip() for w in f.readlines()]
			self.active = (len(self.wordlist) > 0)
		except Exception as e:
			self.log.error(e)
			self.active = False

	def usage(self, msg):
		self.reply(msg, body='usage: "!hangman [a-z]" or "!hangman new"')

	def newGame(self, msg):
		if self.game == None:
			self.game = Game(self.wordlist, self.config['max-guesses'])
			self.reply(msg, body='The game has begun.')
			self.reply(msg, body=self.game.board())
		else:
			self.reply(msg, body='A game of hangman has already begun.')

	def makeGuess(self, msg, char):
		if self.game == None:
			self.reply(msg, body='There is no game ongoing.')
		else:
			result = self.game.guess(char)
			if result == Game.Guess.success:
				self.reply(msg, body='A correct guess!')
				self.reply(msg, body=self.game.board())
			elif result == Game.Guess.failure:
				self.reply(msg, body='Incorrect! >:(')
				self.reply(msg, body=self.game.board())
			elif result == Game.Guess.already:
				self.reply(msg, body='That letter was already guessed!')
			elif result == Game.Guess.gameover:
				text = 'Game over!'
				if random.randint(0,1000) == 0:
					text += ' The executioner pulls the lever, releasing the body from the platform...'

				self.reply(msg, body=text)
				self.reply(msg, body='The word was '+self.game.word)
				self.reply(msg, body=self.game.board())
				self.game = None
			else:
				text = 'Victory!'
				if random.randint(0,100) == 0:
					text += ' The judge has determined your vocabulary is good enough to grant a stay of execution.'

				self.reply(msg, body=text)
				self.reply(msg, body=self.game.board())
				self.game = None

	def receive(self, msg):
		args = msg.body.split(' ')

		if self.active and len(args) >= 1 and args[0] == '!hangman':
			if len(args) != 2:
				self.usage(msg)
			elif args[1] == 'new':
				self.newGame(msg)
			elif len(args[1]) == 1 and args[1][0].isalpha():
				self.makeGuess(msg, args[1][0])
			else:
				self.usage(msg)

