import zulip
import re
import wikipedia
from stackapi import StackAPI

BOT_MAIL = "good-bot@zulipchat.com"


class goodbot(object):
	def __init__(self):
		self.client = zulip.Client(config_file="~/zuliprc")
		self.subscribe_all()
		print("Bot init complete")

	def subscribe_all(self):
		json = self.client.get_streams()["streams"]
		streams = [{"name": stream["name"]} for stream in json]
		self.client.add_subscriptions(streams)
		print("Subscription complete")

	def process(self, msg):
		sender_email = msg["sender_email"]
		if sender_email == BOT_MAIL:  # quick return
			return
		content = msg["content"].split()
		sender_full_name = msg["sender_full_name"]
		message_type = msg["type"]  # "stream" or "private"
		if message_type == "stream":
			destination = msg["display_recipient"]  # destination is PM
		else:
			destination = sender_email  # destination is PM
		topic = msg["subject"]  # topic legacy naming in API

		print(content)

		print("Sucessfully heard.")
		print(msg["content"])

		if "just signed up for" in msg["content"]:
			self.client.send_message({
				"type": message_type,
				"topic": topic,
				"to": "goodbot",
				"content": "Hey " + re.match(r".*\d\*\*\s", msg["content"]).group(0) + " ! Welcome to Wikimedia Zulipchat.\nIf you need any help with GSoC, type `!help gsoc` for help with GSoC proposals.\nType `!help outreachy` for help with Outreachy proposals.\nType `!help` for a full list of available commands. Soon I'll have more features :)"
			})

		if content[0].lower() == "!help" or content[0] == "@**goodbot**":
			if(len(content) == 1):
				self.client.send_message({
					"type": message_type,
					"topic": topic,
					"to": destination,
					"content": "Hey there. :blush: Here's what I can do for you:\nType `!help gsoc` for help with GSoC proposals.\nType `!help outreachy` for help with Outreachy proposals.\nType `!help faq 'your question'` to search FAQs.\nType `!help wikipedia 'title'` to search articles.\nType `!help stackoverflow 'your question'` to search questions."
				})
			elif(len(content) > 1):
				if content[1].lower() == "gsoc":
					self.client.send_message({
						"type": message_type,
						"topic": topic,
						"to": destination,
						"content": "Hello @**" + sender_full_name + "** ! Here's some links to get you started.\nRead the information guide for GSoC participants: https://www.mediawiki.org/wiki/Google_Summer_of_Code/Participants\nRead the project ideas for this year: https://www.mediawiki.org/wiki/Google_Summer_of_Code/2020"
					})
				if content[1].lower() == "outreachy":
					self.client.send_message({
						"type": message_type,
						"topic": topic,
						"to": destination,
						"content": "Hello @**" + sender_full_name + "** ! Here's some links to get you started.\nRead the information guide for Outreachy participants: https://www.mediawiki.org/wiki/Outreachy/Participants\nRead the project ideas for this year: https://www.mediawiki.org/wiki/Outreachy/Round_20"
					})
				if content[1].lower() == "faq":
					if(len(content) == 2):
						self.client.send_message({
							"type": message_type,
							"topic": topic,
							"to": destination,
							"content": "Hello @**" + sender_full_name + "** ! You can ask me a question by adding the question after the command: `!help faq 'your question'`"
						})
					else:
						self.client.send_message({
							"type": message_type,
							"topic": topic,
							"to": destination,
							"content": "Hello @**" + sender_full_name + "** ! In all our projects, we list the level of expertise and skills required. Although you can choose to share your skillset with organization administrators, all they might be able to do is point you to the list of projects you might have seen already on MediaWiki.org. It might be ideal if you assess for yourself which project best suits you based on the skills required, level of expertise needed and any topic area that interests you more. And, this would save everyone some time!"
						})
				if content[1].lower() == "wikipedia":
					self.client.send_message({
						"type": message_type,
						"topic": topic,
						"to": destination,
						"content": "Hello @**" + sender_full_name + "** ! This might take a while to process :time_ticking:"
					})
					query = ' '.join(content[2:])
					self.client.send_message({
						"type": message_type,
						"topic": topic,
						"to": destination,
						"content": "Hey @**" + sender_full_name + "** Got it! :point_right: " + wikipedia.summary(query, sentences=2) + "\n"
					})
					response = ""
					for result in wikipedia.search(query, results=1):
						page = wikipedia.page(result)
						response += ("* [" + page.title + "](" + page.url + ")\n")
					self.client.send_message({
						"type": "stream",
						"topic": topic,
						"to": destination,
						"content": response
					})
				if content[1].lower() == "stackoverflow":
					self.client.send_message({
						"type": message_type,
						"topic": topic,
						"to": destination,
						"content": "Hello @**" + sender_full_name + "** ! This might take a while to process :time_ticking:"
					})
					query = ' '.join(content[2:])
					stackoverflow = StackAPI('stackoverflow')
					stackoverflow.page_size = 3
					stackoverflow.max_pages = 1
					questions = stackoverflow.fetch('search/advanced', sort="relevance", q=query, order="desc", answers=1)
					response = "\n**Closest match:** " + questions['items'][0]['title']
					try:
						answerjson = stackoverflow.fetch('answers/{ids}', ids=[str(questions['items'][0]['accepted_answer_id'])], filter="!9Z(-wzftf")
						answer = "\n**Accepted answer:**\n" + answerjson['items'][0]['body_markdown']
					except IndexError:
						answer = "\n**No accepted answer found**"
					response += answer + "\nOther questions:\n"
					response += '\n'.join(("* [" + question['title'] + "](" + question['link'] + ")") for question in questions['items'][1:])
					self.client.send_message({
						"type": "stream",
						"subject": message_type,
						"to": destination,
						"content": "Hey @**" + sender_full_name + "** Got it! :point_down:\n" + response
					})

		elif "goodbot" in content and content[0] != "!help":
			self.client.send_message({
				"type": "stream",
				"subject": message_type,
				"to": destination,
				"content": "Hey there! :blush: What can I do for you today?"
			})
		else:
			return


def main():
	print("Begin bot init")
	bot = goodbot()
	bot.client.call_on_each_message(bot.process)


if __name__ == "__main__":
	main()