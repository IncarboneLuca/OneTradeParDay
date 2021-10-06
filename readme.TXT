Found a singularity in the stock market, I propose this code allows to compute with past Historical Trade data the good price to buy/sell/stoplosses for given index

THIS IS NOT FINANCIAL ADVICE 

ALL RISKS OF LOSSES WITH TRADING IS UP ON THE BUYER

THIS IS NOT FINANCIAL ADVICE


How to use it, Steps:

conda
	cd C:\Users\xxx\Documents\Py\Index\tradingview
	activate mytrade

run OTAD.py with anaconda mytest environement at 15:25
	python OTAD.py

run record_post_trade.py after 19:00 daily (before next trade)
	python record_post_trade.py

run DDD.py to run the analysis on recorded database to test possible trade and simulate the possible past gain
	python DDD.py