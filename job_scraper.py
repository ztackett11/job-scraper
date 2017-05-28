from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import smtplib
import urllib2

"""
	Author: Zach Tackett
	Email: ztackett11@gmail.com
	Phone: 740-794-0674
"""

def scrape_page(page, soup, keywords):

	"""

	Function scrape_page takes 3 parameters
		page - the page with the job postings
		soup - the BeautifulSoup object created for the page 
		keywords - the keywords to use to perform the match against the job titles on the page(s)

	This function will scrape the page(s), find all of the job postings on the page.
	Using a prefedined keywords list, the func will match the job title against each of the keywords
	To identify if there are any jobs I'd be interested in
	If there is a match, the job title ie "Assistant Webmaster", will be extracted, as well as the direct URL link 
	To the job posting for that title

	Both titles ad links are stored in lists so that later, they can be combined into a dictionary and emailed to my gmail account
	Return the results dictionary to be used in the send_email server

	"""

	# Create 2 empty lists
	# One to hold the job titles and another to hold the links

	job_titles = []
	links = []


	# Create an empty dictionary to hold both the titles and the links for later use

	results = {}


	# Find all of the jobs on the page
	# Uses the BS4 find_all function to find every cell that has the class of job-title

	jobs = soup.find_all("td", class_="job-title")


	# Iterate through all of the jobs

	for job in jobs:


		# Check to see if an href is within the cell

		match = re.search(r'href=[\'"]?([^\'" >]+)', str(job))


		# If the match equates to True

		if match:

			# Get the match and set it to txt

			txt = match.group(0)

			# Split the link into two parts
			# It splits into a list with the 'href=' and the '/postings/{job number}' as strings elements

			href = txt.split('"')

			# href[1] is the second indexed item which is '/postings/{job number}'
			# Append this string to the empty links list

			links.append(href[1])

			# Append the job title string and append it to the job_titles list
			# Strip out any newline characters that are in the string

			job_titles.append(job.text.strip())

	# Create a dictionary that will hold the job titles and links
	# Job_titles is the key
	# Links is the value

	titles_and_links = dict(zip(job_titles, links))

	# String used to concatenate the href from the job posts link
	# ie "https://www.ohiouniversityjobs.com/postings/{job number}"

	jobs_link = "https://www.ohiouniversityjobs.com"

	# Iterate through the dictionary using the iteritems() function call
	# Set title to the job_title and url to the link to the job posting

	for title, url in titles_and_links.iteritems():

		# Iterate through the keywords list

		for kw in keywords:

			# If the keyword is found within the job title

			if kw in title:

				# Add the title ad link to the results dictionary

				results[title] = jobs_link + url

	# Return the results dictionary to be used in the send_email function

	return results



def send_email(results):

	"""

	Function send_email takes 1 parameter
		results = the dictionary containing the job title and link as a key:value pair

	This function takes the dictionary of job titles and links and sends them to me in an email
	Creates the email message and sets the appropriate headers
	Creates a secure connection to the Gmail SMTP server
	identifies me with the Google SMTP servers
	Logs me into my Gmail account
	Sends the email
	Then closes the conection

	"""

	# Gmail username and password login credentials to authenticate with the Google SMTP server

	gmail_user = 'ztackett11@gmail.com'
	gmail_password = '*********'


	# Create message container - the correct MIME type is multipart/alternative.

	msg = MIMEMultipart('alternative')


	# Set the 'Subject' header for the email message

	msg['Subject'] = "Job's scraped from OU's website"


	# Create an empty list to hold the jobs

	jobs_list = []


	# Iterate through ght dictionary containing the job titles and links as key:value pairs
	# Then append them to jobs_list
	# ie the list will be appended as follows: 
	#	["Assistant Webmaster", "https://www.ohiouniversityjobs.com/postings/21336"]

	for title, link in results.iteritems():
		jobs_list.append(title)
		jobs_list.append(link)


	# Iterate through the jobs and join them all together into one string
	# Adding the "<br><br>" on the join adds the tags to the HTML string below
	# This adds whitepace in between the job titles and the links to the job

	jobs = '<br><br>'.join([' ' + job for job in jobs_list])


	# Create the body of the message

	html = """\
	<html>
		<body>
		<h2>Jobs:</h2>
		<hr>
		<h4>%s</h4>
		<hr>
		</body>
	</html>
	""" % (jobs)


	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# The HTML message, is best and preferred.

	part2 = MIMEText(html, 'html')
	msg.attach(part2)

	# Check to see if the beginning of a URL is within the attachment
	# This is to prevent the program from sending out blank emails


	if "https://" in str(part2):


		# Try to create the secure connection to Google's SMTP server
		# Then identify with an ESMTP server
		# Login using the username and password variables from above
		# Send the email to my Gmail account
			# Set the "To", and "From" headers to my email
			# Set the "Message Body" header as the HTML message created above
		# Then close the connection to the server
		# If the try fails, print an error and

		try:
			server = smtplib.SMTP_SSL('smtp.gmail.com')
			server.ehlo()
			server.login(gmail_user, gmail_password)
			server.sendmail(gmail_user, gmail_user, msg.as_string())
			server.close()
		except:
			print 'Something went wrong...'


	# If it equates to False then the blank email will be skipped

	else:
		pass



def main():

	# List of keywords used to match against
	# 

	keywords = ['Developer', 'Engineer', 'IT Security', ' ITIL Process', 'Software', 'Server',
	'Web', 'Web Development', 'Webmaster', 'WordPress', 'Wordpress', 'Web Developer']


	# All of the pages that OU has job postings on.

	# TODO:
		# Could probably set up a for loop to iterate through a given page number
		# Basically just have it look to see if there's no text within the job title like below

	urls = ["https://www.ohiouniversityjobs.com/postings/search?page=1", "https://www.ohiouniversityjobs.com/postings/search?page=2",
		"https://www.ohiouniversityjobs.com/postings/search?page=3", "https://www.ohiouniversityjobs.com/postings/search?page=4", 
		"https://www.ohiouniversityjobs.com/postings/search?page=5"]


	# Create an empty dictionary
	# This is to hold all of the job titles and links to be used in the email later

	jobs = {}


	# Iterate through each of the urls
	# Set each one to 'page'

	for page in urls:


		# Create the BS4 soup object for each page and read the contents

		soup = BeautifulSoup(urllib2.urlopen(page).read())


		# Set job to find out if there are any job postings on the page

		job = soup.find("td", class_="job-title")


		# Check to ensure that there are job postings on the page
		
		if job != None:


			# Get the results from the scrape_page function

			results = scrape_page(page, soup, keywords)


			# Iterate through the results dictionary returned from the scrape_page function
			# Set the title and link
			# Then append them to the jobs dictionary

			# Actually!
				# This may be redundant code
				# Should be able to just send the 'results' dictionary to the send_email function instead of the 'jobs' one

			for title, link in results.iteritems():
				jobs[title] = link


		# If no job postings are found on the page then break from the loop and go on to the next url
		
		else:
			break


	# Send the results to the send_email function

	send_email(jobs)


if __name__ == "__main__":
	main()