# SteveBot
A Discord Bot for managing minecraft server hosted in Azure VM

## Environment setup
* To setup environment variables duplicate .env-example file and rename it to .env
* Modify contents of the file and fill in your values, which you can obtain from steps below

## Setup:
* Discord
  * Go to discord developer portal and create bot
  * Save bot key
  * Enter the key to env file
  ```
  DISCORD_BOT_KEY=
  ```
* Amazon S3
  * Create and setup your AWS account 
  * Go to S3 section
  * Generate private bucket with write permissions
  ```
  AWS_ACCESS_KEY_ID=
  AWS_ACCESS_KEY_SECRET=
  S3_BUCKET_NAME=
  ```
* Azure
  * Enable subscription for your Azure account
  * Create resouce group
  * Create disk and virtual machine running linux
  * Generate ssh keypair and install it on the vm
    * Rename private key to sshkey and put it on your S3 bucket 
  * Enter the specified values in env file
  ```
  AZURE_WORKGROUP=
  AZURE_VM_NAME=
  SERVER_ADDRESS=
  SERVER_USERNAME=
  SERVER_HOST=
  ```
* MC server and Rcon
  * Put your MC server folder in home directory
  * Configure your MC server as you would usually do
  * Rename you startup script to `start.sh`
  * In server.properties enable rcon and provide some secret for authentication
  * Enter the rcon secret to your env file
  ```
  RCON_SECRET=
  ```

## Deployment
There is a few ways to run you discord bot
* Heroku (recommended)
  * Create account
  * Create project for hosting bot
  * Setup environment variables according to your .env file in Heroku
  * Push the source code to Heroku
* Docker (recommended)
  * Install docker
  * Clone source code
  * Run docker compose up
* Local (for development)
  * Clone source code
  * Setup virtual env
  * Install requirements
  * Run App.py
