import os
import logging
from xml.dom.minidom import Document 
from dotenv import load_dotenv

import logging 
import os, json

from util.FileUtil import FileUtil
from util.ConfigUtil import ConfigUtil
from util.DictionaryUtil import DictionaryUtil
from util.JsonUtil import JsonUtil
from util.ExcelUtil import ExcelUtil
from util.MathUtil import MathUtil
from CommonConstants import *

class WebhookEnviziMapping(object):

    def __init__(
        self,
        fileUtil: FileUtil,
        configUtil: ConfigUtil
    ) -> None:
        self.fileUtil = fileUtil
        self.configUtil = configUtil
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())
        self._init_config()

    def _init_config(self):
        self.DATA_STORE_FOLDER = os.getenv("DATA_STORE_FOLDER") 
        self.WEBHOOK_FOLDER = self.DATA_STORE_FOLDER + "/webhook/"
        self.WEBHOOK_FILE = self.WEBHOOK_FOLDER + "/webhook.json"
        self.excelUtil = ExcelUtil()

    def map_webhook_data_to_envizi_format(self, webhook_detail_data, webhook_execute_response) : 
        fieldsArray = webhook_detail_data["fields"]
        data_template_type = webhook_detail_data["data_template_type"]

        processed_data = []
        if (data_template_type == "1-single") :
            processed_data = self._map_webhook_type_1(webhook_execute_response, fieldsArray)
        elif (data_template_type == "2-multiple") :
            processed_data = self._map_webhook_type_2(webhook_execute_response, fieldsArray)
        elif (data_template_type == "3-multiple-and-common") :
            multiple_records_field = DictionaryUtil.getValue_key1(webhook_detail_data, "multiple_records_field", "")

            ### Get mutliple records data field
            multiple_records_field_data = DictionaryUtil.findValue(webhook_execute_response, multiple_records_field)            
            processed_data = self._map_webhook_type_3(webhook_execute_response, multiple_records_field_data, fieldsArray)

        return processed_data


    def _map_webhook_type_common(self, webhook_data, webhook_row_data, fieldsArray):
        self.logger.info("map_webhook_type_common  ... ")

        result_row_data = {}

        ### Create Data
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "organization")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "record_start")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "record_end")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "account_supplier")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "location")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "account_style")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "account_name")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "account_ref")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "account_supplier")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "record_start")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "record_end")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "quantity")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "total_cost")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "record_reference")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "record_invoice_number")
        self._processFieldValue(webhook_data, webhook_row_data, result_row_data, fieldsArray, "record_data_quality")
        
        return result_row_data


    def _map_webhook_type_1(self, webhook_data, fieldsArray):
        self.logger.info("map_webhook_type_1  ... ")

        processed_data = []
        result_row_data = self._map_webhook_type_common (webhook_data, None, fieldsArray)
        processed_data.append(result_row_data)

        return processed_data


    def _map_webhook_type_2(self, webhook_data, fieldsArray):
        self.logger.info("map_webhook_type_2  ... ")

        processed_data = []
        for webhook_row_data in webhook_data :
            result_row_data = self._map_webhook_type_common (webhook_data, webhook_row_data, fieldsArray)
            processed_data.append(result_row_data)

        return processed_data


    def _map_webhook_type_3(self, webhook_data, multiple_records_field_data, fieldsArray):
        self.logger.info("map_webhook_type_3  ... ")

        processed_data = []
        for webhook_row_data in multiple_records_field_data :
            result_row_data = self._map_webhook_type_common (webhook_data, webhook_row_data, fieldsArray)
            processed_data.append(result_row_data)

        return processed_data

    # def _processFieldValue(self, webhook_data, webhook_row_data, result_row_data, fieldsArray, fieldName) : 
    #     item = JsonUtil.findElement(fieldsArray, "name", fieldName)
    #     label = item["label"]
    #     mapValue = item["map_value"]

    #     resultValue = None
    #     ### If row_data is not empty..then try in row_data first
    #     if (webhook_row_data != None) :
    #         resultValue = DictionaryUtil.findValue(webhook_row_data, mapValue)

    #     ### If returned data is empty from the previous try, then try in webhook_data
    #     if (resultValue == None) :
    #         resultValue = DictionaryUtil.findValue(webhook_data, mapValue)

    #     result_row_data[label] = resultValue

    def _processMapValue(self, webhook_data, webhook_row_data, mapValue) : 
        resultValue = None
        ### If row_data is not empty..then try in row_data first
        if (webhook_row_data != None) :
            resultValue = DictionaryUtil.findValue(webhook_row_data, mapValue)

        ### If returned data is empty from the previous try, then try in webhook_data
        if (resultValue == None) :
            resultValue = DictionaryUtil.findValue(webhook_data, mapValue)

        return resultValue

    def _processFieldValue(self, webhook_data, webhook_row_data, result_row_data, fieldsArray, fieldName) : 
        item = JsonUtil.findElement(fieldsArray, "name", fieldName)
        label = item["label"]
        map_value = item["map_value"]
        text_value = item["text_value"]
        list_value = DictionaryUtil.getValue_key1(item, "list_value", "")
        result = ""
        
        self.logger.info(f"_processFieldValue text_value : {text_value},    map_value : {map_value}")

        if (text_value != "") :
            result = text_value
        elif (list_value != "") :
            result = list_value
        elif (map_value != "") :
            result = self._processMapValue(webhook_data, webhook_row_data, map_value)
        else :
            firstRecord = True
            operation_value_prev = ""
            for subItem in item["list"] :
                text_value = subItem["text_value"]
                map_value = subItem["map_value"]
                list_value = DictionaryUtil.getValue_key1(subItem, "list_value", "")
                operation_value = DictionaryUtil.getValue_key1(subItem, "operation_value", "")

                curr_value = ""
                if (text_value != "") :
                    curr_value = text_value
                elif (list_value != "") :
                    curr_value = list_value
                elif (map_value != "") :
                    curr_value = self._processMapValue(webhook_data, webhook_row_data, map_value)

                if (firstRecord) :
                    firstRecord = False
                    result = curr_value
                else :
                    if (operation_value_prev == "Append") :
                        result = str(result) + str(curr_value)
                    elif (operation_value_prev == "+") :
                        result = MathUtil.add_or_append(result, curr_value) 
                    elif (operation_value_prev == "-") :
                        result = MathUtil.sub_or_append(result, curr_value) 
                    elif (operation_value_prev == "*") :
                        result = MathUtil.mul_or_append(result, curr_value) 
                    elif (operation_value_prev == "/") :
                        result = MathUtil.divide_or_append(result, curr_value) 
                    else :
                        result = str(result) + str(curr_value)

                operation_value_prev = operation_value

        result_row_data[label] = result



    def getTemplateColumns(self) :
        ### template_columns
        ### TODO - POC/ASDL-PMC check to tbe done.
        template_file_name = os.getenv("DATA_FOLDER", "") + "/templates/POCAccountSetupandDataLoad_template.xlsx"
        self.logger.info("loadTemplate template_file_name ... : " + template_file_name)
        template_columns = self.excelUtil.readColumnName(template_file_name)
        return template_columns
    