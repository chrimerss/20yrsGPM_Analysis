import requests
from bs4 import BeautifulSoup
import re
import os
import multiprocessing
import warnings
warnings.simplefilter("ignore")


def get_dates(url):
	
	response= requests.get(url, allow_redirects= True)
	contents= response.content
	soup= BeautifulSoup(contents)
	dates= soup.find_all('a')
	# find dates in the index
	verified_dates= []
	parttern_date= r'20[0-9][0-9]'
	for date in dates:
		res= re.match(parttern_date, date.text)
		if res is not None:
			verified_dates.append(res.group())
	
	return verified_dates

def retrieve_h5(year, day, url):
	child_url= url+'/%s/%s'%(str(year),str(day))
	response= requests.get(child_url, allow_redirects=True)
	if response.status_code== 200:
		print('%s-%s successfully connected!'%(year,day))
	else:
		raise FileNotFoundError('cannot connect to server: %s, error code: %d'%(child_url, response.status_code))
	soup= BeautifulSoup(response.content)
	files= soup.find_all('a')
	#print(files)
	if files is None:
		raise ValueError('not good connection')
	parttern= r'(3B-HHR-E.MS.MRG.3IMERG.\d{8}-S\d{6}-E\d{6}.\d{4}.\D\d{2}\D.HDF5)'
	verified_files= []

	for f in files:
		res= re.match(parttern, f.text)
		if res is not None:
			f_name= res.group()
			url_file= child_url+'/'+f_name
			date= f_name.split('.')[4]
			with open('%s/%s/%s.HDF5'%(year,day,date), 'wb') as f:
				f.write(requests.get(url_file, allow_redirects=True).content)
		
	return verified_files

def day_retrival(year, url='https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHHE.06'):
	day_url= url+'/%s/'%year
	def get_days(url):
		response= requests.get(url, allow_redirects= True)
		if response.status_code!=200:
			raise FileNotFoundError('cannot connect to server: %s, error code: %d'%(day_url, response.status_code))
		soup= BeautifulSoup(response.content)
		files= soup.find_all('a')
		days= []
		parttern= r'(\d{3})'
		for f in files:
			res= re.match(parttern, f.text)
			if res is not None:
				day= res.group()
				days.append(day)
		return days
	
	days= get_days(day_url)
	if not os.path.exists(str(year)):
		os.mkdir(str(year))

	for day in days:
		if not os.path.exists(os.path.join(str(year),str(day))):
			os.mkdir(os.path.join(str(year),str(day)))
		retrieve_h5(year, day, url)
	print('one year completed')	


def main():
	url= 'https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHHE.06'
	years= get_dates(url)
	pool= multiprocessing.Pool(50)
	pool.map(day_retrival, years)
	
	

if __name__== '__main__':
	main()
