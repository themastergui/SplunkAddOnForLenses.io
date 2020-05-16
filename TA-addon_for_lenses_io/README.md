# Addon for Lenses.io

## Overview

This Addon allows you to query data in a Kafka topic or Elasticsearch index with a SQL command within Splunk. The App sends the query to Lenses.io and it uses Lenses' SQL Engine and permission model to fetch the data.

## Installation

### Pre-requisites 

1. A working Lenses instance connected to at least a Kafka cluster. If you don't have your own Kafka cluster, you can use the all-in-one [Lenses Box Docker Container](https://lenses.io/downloads/lenses/?path=wizard-form) for free

2. An instance of Splunk. You can download [Splunk for free](https://www.splunk.com/en_us/download.html)


## Installation

### Install Lenses.io Python on Splunk instance (Search Head in distributed environment)

Follow the [Lenses.io documentation](https://docs.lenses.io/dev/python-lib/index.html)

### Install the Lenses.io Addon

Place the contents of this Addon into the /opt/splunk/etc/apps/ directory and restart Splunk.

Or install the App as described in the [docs](https://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall)

### Create a Service Account in Lenses.io

In the Admin section of Lenses, create a Group (under User Management). Ensure you assign the necessary permissions in the "data namespace" section to query data from certain topics. Enter a wildcard (*) to allow permissions on all topics

Then, create a Service Account User and assign it to the group that you just created. Take note of the Service Token as you won't get another chance to retrieve it. You don't need to set an Owner. 

Also take note of the Service Account Name of the user you just created. You security token you'll need in Splunk will be:

<name of service account>:<token>
eg:  MyUser:a874a238-0024-47d2-b8f4-e9fc74fa8488

### Configure the Addon in Splunk

In Splunk, go to the Addon App (http://<splunkhost:<port>/en-GB/app/TA-addon_for_lenses_io/) Configuration. You'll need to click on the "Add-on Settings" tag and assign the Service Account token and Lenses instance URL:

Lenses.io Service Account = <Service Account User>:<Token>
Lenses.io URL = http://<lenses.io host>:<lenses.io port>

Click Save

## Run a search

Go to a Search bar. 

The command for lenses is:

lensesiosearch

The search must be the first command in a search and prefixed with a pipe (|). Example: | lenses.io

It takes one parameter which is the SQL command. 

| lensesiosearch sql="select currency, amount from cc_payments LIMIT 10"

If you're using Lenses Box, that exact query should work

## Troubleshooting

Ensure you look at the search.log in the Search inspector (Under the "job" dropdown in a Splunk search bar)if you get any errors  
