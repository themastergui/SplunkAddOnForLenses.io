# Addon for Lenses.io

## Overview

In beta.

This Addon allows you to query data in a Kafka topic or Elasticsearch index with a SQL command within Splunk. The App sends the query to Lenses.io and it uses Lenses' SQL Engine and permission model to fetch the data.

It has been tested on Splunk 8.0.3 and Lenses.io 3.1. The script should work with both free versions of Lenses.io (easiest is to get free Cloud Sandbox environment which  includes an instance of Kafka at http://portal.lenses.io/. Alternatively you can use the Lenses.io "Box" docker container) and Splunk Enterprise or Splunk Cloud (https://www.splunk.com/en_us/download.html)

The AddOn is at very early stages of development. It's biggest limitation is it's only designed to returned small data sets back to Splunk (around maximum of 1000 results). Please do not use in production but provide feedback to guillaume.ayme@gmail.com

Improvements to be made:
+ Better error handling
+ Better security
+ Able to manage larger results sets

## Installation

### Pre-requisites 

1. A working Lenses instance connected to at least a Kafka cluster. If you don't have your own Kafka cluster, you can use the all-in-one [Lenses Box Docker Container](https://lenses.io/downloads/lenses/?path=wizard-form) or the Lenses.io [Cloud Sandbox](http://portal.lenses.io/) for free

2. An instance of Splunk. You can download [Splunk for free](https://www.splunk.com/en_us/download.html)


## Installation

### Install Lenses.io Python on Splunk instance (Search Head in distributed environment)

You must use Python3.

First, install PIP3

```console
sudo apt install python3-pip 
```

Clone Lenses.io Python Client from Github

```console
sudo git clone https://github.com/lensesio/lenses-python.git
```

Enter into the lenses-python dir

```console
cd lenses-python
```

Build the Lenses.io Python lib

```console
sudo python3 setup.py sdist bdist_wheel
```

Install the lib

```console
sudo pip3 install dist/lensesio-3.0.0-py3-none-any.whl
```

Install Pulsar lib

```console
sudo pip3 install pulsar
```

Full instructions can be found here [Lenses.io documentation](https://docs.lenses.io/dev/python-lib/index.html)


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

```
lensesiosearch
```

The search must be the first command in a search and prefixed with a pipe (|). Example: | lenses.io

It takes one parameter which is the SQL command. 

```
| lensesiosearch sql="select currency, amount from cc_payments LIMIT 10"
```

If you're using Lenses Box, that exact query should work

## Troubleshooting

### Test the script outside of Splunk

If the custom command isn't working, you can test running the bin/lenses.py script which is the main script called by the lensesCustomCommandWrapper.py script outside of Splunk.  Connect to your Splunk instance and go to:

```console
cd $SPLUNK_HOME/etc/apps/TA-addon_for_lenses_io/bin
```

Create an environment variable with the value of the security token from Lenses.io. Again, ensure token is prefixed by the owner of the token in Lenses.io (in example below it's "Splunk2")

```console
export LENSES_TOKEN=Splunk2:b331cef8-55ad-71e5-8c7f-5fdbfe41d1e9
```

Run the command:

```console
python3 -E lenses.py -c LENSES_TOKEN -u https://amazing-bose.portal.lenses.io -s "select amount, currency from cc_payments LIMIT 100"
```

There should be a large standard out dump of raw data returned by the SQL command. If so, the script works.

### Pulsur Error when running search

```console
Traceback (most recent call last):
 File "lenses.py", line 3, in <module>
  from lensesio.lenses import main as lenses
 File "/usr/local/lib/python3.6/dist-packages/lensesio/lenses.py", line 18, in <module>
  from lensesio.pulsar.pulsar_client import SetupPulsar
 File "/usr/local/lib/python3.6/dist-packages/lensesio/pulsar/pulsar_client.py", line 1, in <module>
  import pulsar
ModuleNotFoundError: No module named 'pulsar'
```

Make sure you have installed the Pulsar package in Python

```console
sudo pip3 install pulsar
```


### Other troubleshooting

Ensure you look at the search.log in the Search inspector (Under the "job" dropdown in a Splunk search bar)if you get any errors  

For any issues with the App, contact guillaume.ayme@gmail.com, Guillaume Ayme on LinkedIn or @lemastergui on Twitter


