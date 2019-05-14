from bs4 import BeautifulSoup
import requests, urllib3
import praw
import time
import re
import os.path


langMasterKey = {'hi':'Hindi','bn':'Bengali','te':'Telugu',
'mr':'Marathi','ta':'Tamil','gu':'Gujarati',
'ur':'Urdu','kn':'Kannada','or':'Odia',
'ml':'Malayalam','pa':'Punjabi','as':'Assamese'}


def authenticate():
	reddit = praw.Reddit('indianWikiBot', user_agent = "IndianWikiBot v0.1")
	print("Authenticate as {}".format(reddit.user.me()))
	return reddit


def checkComments(reddit,commentsRepliedTo):
	for comment in reddit.subreddit('pythonforengineers').comments(limit=25):
		# if "bag" in comment.body:
		# 	print("comment with \"bag\" Found in comment" + comment.id)
		# 	print(comment.body_html)
		if not any(link in str(comment.body).lower() for link in ["en.wikipedia.org/wiki/", "en.m.wikipedia.org/wiki/"]):
			return
		if comment.id in commentsRepliedTo:
			break
		urls = linksToWikis(comment.body_html)
		# print(urls)

		collectedLinks = linksToIndianWikis(urls)
		# print(collectedLinks)
		print("1")
		commentText =  replies(collectedLinks)

		comment.reply(commentText)
		commentsRepliedTo.append(comment.id)

		with open ("commentsRepliedTo.txt","a") as file:
			file.write(comment.id + "\n")

		# linksToIndianWikis(urls)


def linksToWikis(text):

	soup = BeautifulSoup(text,'lxml')

	urls1 = []

	# get all links from comments
	for url in soup.findAll('a'):
		try:
			urls1.append(url['href'])
		except Exception as e:
			pass

	urls2 = []

	# delete Duplicate links
	for url in urls1:
		if url not in urls2:
			urls2.append(url)

	urls1 = []

	#Keep wikipedia links only
	for url in urls2:
		if "wikipedia.org/wiki/" in url:
			urls1.append(url)

	urls2 = []

	#change Mobile links to Desktop links
	pattern = ".m.wikipedia.org/wiki/"
	replace = ".wikipedia.org/wiki/"

	for url in urls1:
		url =  re.sub(pattern,replace,url)
		urls2.append(url)

	soup.decompose()

	return urls2


def linksToIndianWikis(wikiList):
	finalList = {}
	for url in wikiList:
		wiki = url

		page = requests.get(wiki).text
		soup = BeautifulSoup(page,'lxml')

		heading = soup.find('h1',id="firstHeading").text

		#block of languages
		langBlock = soup.find('div', id="p-lang")
		listOfLangs = langBlock.ul

		langTempKey = {}

		for language in listOfLangs.find_all('li'):
		   languageTag = language.a['lang']
		   languageLink = language.a['href']
		   if languageTag in langMasterKey:
		      langTempKey[langMasterKey[languageTag]] = languageLink
		##      print(languageTag)
		##      print(languageLink)
		      # print("")

		finalList[heading] = langTempKey

		soup.decompose()

	return finalList


def replies(collectedLinks):
	commentText = ""
	for collection in collectedLinks:
		commentText += "##{}\n\n***\n\n".format(collection)
		linksForThis = collectedLinks[collection]
		for link in linksForThis:
			commentText += "[{}]({}) ".format(link,linksForThis[link])
		commentText += "\n\n"

	commentText += "\n\n***\n\nThis is a Bot."

	return commentText

def repliedTo():
	if not os.path.exists('commentsRepliedTo.txt'):
		commentsRepliedTo = []
	else:
		with open("commentsRepliedTo.txt", "r") as file:
			commentsRepliedTo = file.read()
			commentsRepliedTo = commentsRepliedTo.split("\n")

	return commentsRepliedTo

		
def main():
	reddit = authenticate()
	commentsRepliedTo = repliedTo()
	#while(True):
	checkComments(reddit,commentsRepliedTo)

if __name__ == '__main__':
	main()