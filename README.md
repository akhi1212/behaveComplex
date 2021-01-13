### **alps-qa-aut-testing**

==================

This framework is created for Automation tests coverage purpose.

#### **Setup**

Prerequisites:

Python 3.8 or above (you can find guide on Python installation here https://realpython.com/installing-python/)

#### **Configuration**

Install virtualenv:
```
$ pip install virtualenv
```
Setup virtual environment:
```
$ virtualenv venv
```
Activate the virtualenv:
```
$ source venv/bin/activate
```
Install dependencies:
1. JDK  
    ```    
    $ sudo apt install openjdk-8-jdk-headless docker docker-compose gradle awscli
   ```

2. Android SDK  
   ```
   sudo apt install android-sdk
   wget https://dl.google.com/android/repository/commandlinetools-linux-6858069_latest.zip
   unzip commandlinetools-linux-6858069_latest.zip
   sudo rsync -va cmdline-tools/ /usr/lib/android-sdk/tools/
    ```
3. Node JS  
   ```
    sudo apt-get install nodejs
   ```

4. Appium
    ```
    sudo apt-get install npm
    sudo npm install -g appium
    sudo npm install -g appium-doctor
    ```
    go to https://github.com/appium/appium-desktop/releases/latest 
    download the Latest releases's AppImage. It should be something like *Appium-linux-\<latest version>.AppImage*   
    ```    
    chmod a+x Appium-linux-<latest version>.AppImage
    ./AppImage
    ```

5. Set environment variables
    ```
    sudo nano ~/.bashrc
    export ANDROID_HOME=/usr/lib/android-sdk
    export ANDROID_SDK_ROOT=$ANDROID_HOME
    export PATH=$PATH:$ANDROID_HOME/tools/bin
    export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
    source ~/.bashrc
    ```

Install requirements:
```
$ pip install -r requirements.txt
```

##### **Local Run**

In case of run against local environment please execute below docker command from 'alps_docker_aws' folder to setup localhost environment pointing to local dynamoDB database

```
$ cd alps_docker_aws
$ sudo ./docker-start.sh
```
Also, if the application runs for the first time you need initialize dynamo DB tables. For that run the init script:
 ```
$ ./init_dynamodb_tables.sh
 ```
as a result, you will see a list of currently available tables.

##### **E2E Run (with device check)**
Before run activate debugging on the device and connect it to adb over usb or wifi. Over usb is preferable
Make sure the device IMEi and serial number is in /config/test4_qa_config (not required if the device is connected)
See details how to setup in https://developer.android.com/studio/command-line/adb

Run Appium Desktop.  
On the tab "Advanced" check the "Relaxed security".  
Run the server on the default port.  
Later, when the test will be running, you'll be able to attach to the session: `File` -> `New session window` -> `Attach to session`



#### **Tests execution:**

Add root directory to PYTHONPATH:
```
  $ export PYTHONPATH=./alps-qa-api
```
Run all tests:
```
  $ behave -D environment=local
```
Run a separate feature tests:
```
  $ behave tests/public_api.feature
```
Run specified scenario:
```
  $ behave -n "Scenario Name"
```
Run tests by tags expression:
```
  $ behave --tags="@tag_name"
```

#### Tags:

###### Feature tags  
   * `API_Tests` - to run API test suites
   * `E2E_Tests` - starts Selenium webdriver and Appium webdriver (if tag `no_device` is not used)
   * `ALPS_Client` - alps client related tests
   * `KNOX_GUARD` - tests with Samsung Knox Guard devices

###### Scenario tags
   * `ATP-XXX` - test case tag( same as ticket key from Jira)
   * `no_device` - cancels starting Appium webdriver, even if  `E2E_Tests` tag is used
   * `slow` - tag for tests with over than average run duration (e.g. api tests with automated transition)
   * `env:<env_type>` - if present than test will run only on specified env_type(e.g. @env:test4_qa)

#### CLI arguments:
* ##### loglevel
  > If used, overrides the config.log_level  
  > **Options**: any level from python's logging lib  
  > **Default**: `config.log_level`  
  > **Example**: `-D loglevel=DEBUG`  
  
* ##### environment
  > Defines which environment the tests will be run against 
  > **Options**:
  > * `local` - runs tests against locally deployed microservices 
  > * `test4_qa`  - runs tests against https://test4.qa.trustonic-alps.com 
  > * `test5_qa`  - runs tests against https://test5.qa.trustonic-alps.com 
  > 
  > **Default**: `local`  
  > **Example**: `-D environment=test4_qa`
