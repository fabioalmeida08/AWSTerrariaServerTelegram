from telebot import types
import telebot
import json
import boto3
from mypy_boto3_ec2 import EC2Client
from mypy_boto3_ssm import SSMClient
from typing import Any, Dict
import os

class Boto3Client:
    def __init__(self):
        self.ssm: SSMClient = boto3.client("ssm")
        self.ec2: EC2Client = boto3.client("ec2")

    def get_parameter(self, name: str, with_decryption: bool = True) -> str:
        return self.ssm.get_parameter(Name=name, WithDecryption=with_decryption)[
            "Parameter"
        ]["Value"]



class TelegramBotHandler:
    def __init__(self, bot_token: str):
        self.bot = telebot.TeleBot(bot_token, threaded=False)
        self.client = Boto3Client()
        self.setup_handlers()
        self.bucket_name = os.getenv("BUCKET_NAME")


    def setup_handlers(self):
        @self.bot.message_handler(commands=["ls"])
        def list_instances(message):
            """
            method triggers after the user send the command /ls to the bot.
            the bot send the webhook request to be precessed here
            """
            self._list_instances(message, self.bot)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_handler(callback):
            """
            method responsible to process the action after one of
            the instances are manually selected by the user.
            is necessary create a new markup menu to update the message in place
            """
            callback_data = json.loads(
                callback.data
            )  # eg. {"action": action1, "id": "instance_id"}
            chat_id = callback.message.chat.id
            message_id = callback.message.message_id
            instance = self._get_ec2_instances(callback_data["id"])
            """
            need to create a new markup to update the message with markup
            https://core.telegram.org/bots/api#updating-messages
            """
            new_markup = self._create_menu_markup(
                instance[0]["id"]
            )  

            if callback_data.get("action") == "menu":
                if instance[0]["state"] == "running":
                    self.bot.edit_message_text(
                        f"🖥️  🟢  {instance[0]['name']} Menu:",
                        chat_id,
                        message_id,
                        reply_markup=new_markup,
                    )
                elif instance[0]["state"] == "stopped":
                    self.bot.edit_message_text(
                        f"🖥️  🔴  {instance[0]['name']} Menu:",
                        chat_id,
                        message_id,
                        reply_markup=new_markup,
                    )
                elif instance[0]["state"] == "stopping":
                    self.bot.edit_message_text(
                        f"🖥️  🟠  {instance[0]['name']} Menu:",
                        chat_id,
                        message_id,
                        reply_markup=new_markup,
                    )

            elif callback_data.get("action") == "change_state":
                #TODO: adicionar autenticaçao para realizar essa ação
                if instance[0]["state"] == "running":
                    self.client.ec2.stop_instances(InstanceIds=[callback_data["id"]])
                    self.bot.edit_message_text(
                        "🖥️  🟠 Stopping Instance",
                        chat_id,
                        message_id,
                        reply_markup=new_markup,
                    )
                else:
                    self.client.ec2.start_instances(InstanceIds=[callback_data["id"]])
                    self.bot.edit_message_text(
                        "🖥️  🟢 Starting Instance",
                        chat_id,
                        message_id,
                        reply_markup=new_markup,
                    )

            elif callback_data.get("action") == "get_ip":
                self.bot.edit_message_text(
                    "🖥️ Instance IP sent", chat_id, message_id, reply_markup=new_markup
                )
                self.bot.send_message(chat_id, f"Public IP: {instance[0]['public_ip']}")

            elif callback_data.get("action") == "list":
                self.bot.edit_message_text(
                    "🖥️ Instances:",
                    chat_id,
                    message_id,
                    reply_markup=self._create_list_markup(),
                )
            elif callback_data.get("action") == "backup":
                print("backup") 
                self._backup_world(callback_data["id"],chat_id,message_id)
                
                print(callback.message.from_user.id)

    def _create_menu_markup(self, instance_id):
        """
        this function is responsible to create the menu context after
        the instance is select from command /list eg.:
        +-------------------------+-------------------------+
        |                   Instance Name                   |
        +-------------------------+-------------------------+
        |     Change State        |        Get IP           |
        +-------------------------+-------------------------+
        |          💾             |          ↩️              |
        +-------------------------+-------------------------+
        """
        markup = types.InlineKeyboardMarkup(row_width=2)
        opt1_callback = self._create_callback_data("change_state", instance_id)
        opt1 = types.InlineKeyboardButton("⏯️", callback_data=opt1_callback)
        opt2_callback = self._create_callback_data("get_ip", instance_id)
        opt2 = types.InlineKeyboardButton("🌐 IP", callback_data=opt2_callback)
        opt3_callback = self._create_callback_data("backup", instance_id)
        opt3 = types.InlineKeyboardButton("💾", callback_data=opt3_callback)
        opt4_callback = self._create_callback_data("list")
        opt4 = types.InlineKeyboardButton("↩️", callback_data=opt4_callback)
        markup.add(opt1, opt2, opt3, opt4)
        return markup

    def _create_list_markup(self):
        """
        this function create the markup menu with buttons
        to list instances of the aws account if the required lambda
        role allow it.
        The instances are shown with an icon corresponding
        to the actual state of the instance.
        +-------------------------+
        |    🖥️ 🟢 Instance 1     |
        +-------------------------+
        |    🖥️ 🔴 Instance 2     |
        +-------------------------+
        after clicking on the menu button of the instance,
        the create_callback_data method creates a json string
        with the option and instanceID to query handler method to process it
        """
        instances = self._get_ec2_instances()
        markup = types.InlineKeyboardMarkup(row_width=2)

        for instance in instances:
            callback_data = self._create_callback_data("menu", instance["id"])
            if instance["state"] == "running":
                opt = types.InlineKeyboardButton(
                    f"🖥️  🟢 {instance["name"]}", callback_data=callback_data
                )
                markup.add(opt)
            if instance["state"] == "stopped":
                opt = types.InlineKeyboardButton(
                    f"🖥️  🔴 {instance["name"]}", callback_data=callback_data
                )
                markup.add(opt)
            if instance["state"] == "stopping":
                opt = types.InlineKeyboardButton(
                    f"🖥️  🟠 {instance["name"]}", callback_data=callback_data
                )
                markup.add(opt)
        return markup

    def _get_ec2_instances(self, instance_id=None):
        """
        this method return a list of dicts with instances datas
        if the 'instance_id' parameter are provided
        just a list with one instance and instance data
        """
        ec2 = self.client.ec2
        if instance_id:
            response = ec2.describe_instances(InstanceIds=[instance_id])
        else:
            response = ec2.describe_instances()
        instances = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                tags = instance.get("Tags", [])
                name = ""
                for tag in tags:
                    if tag["Key"] == "Name":
                        name = tag["Value"]
                instance_data = {
                    "id": instance["InstanceId"],
                    "state": instance["State"]["Name"],
                    "public_dns": instance.get("PublicDnsName", "N/A"),
                    "public_ip": instance.get("PublicIpAddress", "N/A"),
                    "name": name,
                }
                instances.append(instance_data)
        return instances

    def _create_callback_data(self, action, id=None):
        """
        this function is responsible to
        create a json string with the 'action' and instance id
        of the instance selected from the menu markup
        """
        callback = {"action": action, "id": id}
        return json.dumps(callback)

    def _list_instances(self, message, bot):
        """
        this method send the message to to user with this format
        +-------------------------+
        | 🖥️ Instances:           |
        +-------------------------+
        |    🖥️ 🟢 Instance 1     |
        +-------------------------+
        |    🖥️ 🔴 Instance 2     |
        +-------------------------+
        """
        markup = self._create_list_markup()
        bot.send_message(message.chat.id, "🖥️ Instances:", reply_markup=markup)

    def _process_event(self, event: Dict[str, Any]):
        request_body_dict = json.loads(event["body"])
        update = telebot.types.Update.de_json(request_body_dict)
        self.bot.process_new_updates([update])

    def _backup_world(self,instance_id,chat_id,message_id):
        try:
            # Enviar o comando para a instância
            if self.bucket_name:
                response = self.client.ssm.send_command(
                    InstanceIds=[instance_id],
                    DocumentName="AWS-RunShellScript",
                    Parameters={
                        'commands': [f"aws s3 cp /home/ubuntu/.local/share/Terraria/Worlds s3://{self.bucket_name}/Worlds --recursive"]
                    },
                )
                
                self.bot.edit_message_text(
                    "✅ 🗑️ Backup Success",
                    chat_id,
                    message_id,
                    reply_markup=self._create_list_markup(),
                )
                return response

        except Exception as e:
            print(f"Error : {str(e)}")
            self.bot.edit_message_text(
                    "⚠️ Something went wrong, check logs.",
                    chat_id,
                    message_id,
                    reply_markup=self._create_list_markup(),
                )
            return None

    def lambda_handler(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        print("event ---->", event)
        self._process_event(event)
        return {"statusCode": 200}
