import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from io import BytesIO
from data_sumary import summarize_data
import createAgentsOPENAI
import re
import warnings
import time
import os
from PyQt5.QtCore import QObject, pyqtSignal, QThread
# 统计和时间序列分析库
import statsmodels.api as sm
from statsmodels.tsa import api as tsa



database_information = None

previous_code = None

codesequence = []


class WorkflowThread(QThread):
    def __init__(self, workflow):
        super().__init__()
        self.workflow = workflow
    
    def run(self):
        self.workflow.run()

    def stop(self):
        """强制停止线程"""
        self.workflow.running = False
        self.workflow.query_from_customer = None
        self.terminate()  # 强制终止线程
        self.wait()      # 等待线程结束



class Workflow(QObject):
    # 定义信号
    message_signal = pyqtSignal(str, bool)  # (消息内容, 是否是用户消息)
    data_signal = pyqtSignal(object, bool)  # 用于发送DataFrame
    conversation_mode_signal = pyqtSignal(bool)  # 新增信号
    codesequence_signal = pyqtSignal(object)
    previous_code_signal = pyqtSignal(object)
    database_information_signal = pyqtSignal(object)
    seeking_mode_signal = pyqtSignal()  
    operating_mode_signal = pyqtSignal()
    back_to_thinking_mode_signal = pyqtSignal()  

    
    def __init__(self):
        super().__init__()
        # 初始化agents
        self.customer_service_agent = createAgentsOPENAI.CustomerServiceAgent()
        self.task_summary_agent = createAgentsOPENAI.TaskSummaryAgent()
        self.data_analysis_agent = createAgentsOPENAI.DataAnalysisAgent()
        self.bugfinder_agent = createAgentsOPENAI.BugFinderAgent()
        self.adjustment_agent = createAgentsOPENAI.AdjustmentAgent()
        self.response_from_dataanalyst = None
        self.responseofda = None
        self.query_from_customer = None
        self.customer_service_response = None
        self.task_summary_response = None
        self.data_analysis_response = None
        self.double_check = 0
        self.status = 0
        self.last_status = None
        self.conversation_button = True
        self.running = True
        self.result_df = None
        self.df = None
        self.ds = None




    def clear_memory(self):
        """清理所有状态"""
        self.running = True
        self.query_from_customer = None
        self.status = 0
        self.customer_service_agent = createAgentsOPENAI.CustomerServiceAgent()
        self.task_summary_agent = createAgentsOPENAI.TaskSummaryAgent()
        self.data_analysis_agent = createAgentsOPENAI.DataAnalysisAgent()
        self.bugfinder_agent = createAgentsOPENAI.BugFinderAgent()
        self.response_from_dataanalyst = None
        self.responseofda = None
        self.customer_service_response = None
        self.task_summary_response = None
        self.data_analysis_response = None
        self.double_check = 0
        self.last_status = None
        self.conversation_button = True
        self.result_df = None
        self.df = None
        self.ds = None
        self.conversation_mode_signal.emit(True)  # 新增重置信号
        self.database_information_signal.emit(None)
        self.previous_code_signal.emit(None)
        self.codesequence_signal.emit([])




    def import_data(self,DF):
        self.df = DF
        self.df.columns = self.df.columns.str.replace(r'[\n\r\t]', '', regex=True)

    def set_ds(self,DS):
        self.ds = DS

    @staticmethod
    def api_call_with_retry(func, *args, **kwargs):
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            response = func(*args, **kwargs)
            
            # 检查返回值是否包含错误信息
            if isinstance(response, dict):
                # 检查所有值是否包含Error
                has_error = any('rror: ' in str(value) or 'onnect' in str(value) for value in response.values())
                if not has_error:
                    return response
            elif isinstance(response, str):
                if 'rror: ' not in response and 'onnect' not in response:
                    return response
                
            retry_count += 1
            if retry_count == max_retries:
                print(f"API调用失败，连续{max_retries}次返回错误")
                return response
            print(f"API返回错误，正在进行第{retry_count}次重试...")
            time.sleep(2)  # 重试前等待2秒

    def run(self):
        while self.running:
            if self.status == 0:
                # 发送会话模式信号
                self.conversation_mode_signal.emit(True)  # 新增
                self.conversation_button = True

                # 删除 input() 调用，改为等待 query_from_customer 被设置
                while self.query_from_customer is None and self.running:
                    time.sleep(0.5)  # 短暂休眠避免CPU占用过高
                
                if not self.running:
                    break
                    
                self.conversation_button = False
                # 发送会话模式信号
                self.conversation_mode_signal.emit(False)  # 新增
                self.conversation_button = False
                print("AI查看数据库中（RAG）...")

                self.seeking_mode_signal.emit()

                temp_query = self.query_from_customer  # 保存当前查询
                self.query_from_customer = None  # 重置查询，为下一次输入做准备
                
                temp_history = self.customer_service_agent.history + [{
                        "role": "顾客",
                        "content": temp_query
                    }]
                temp_history = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in temp_history[-min(5, len(temp_history)):]
                ])
                database_info = summarize_data(self.df,self.ds,temp_query)

                database_information = database_info
                self.database_information_signal.emit(database_information)

                #在接入rag后，顾客每次说话都需要更新database_info
                self.last_status = 0
                self.status = 2
                '''if self.status == 1:
                #数据分析师说话

                self.query_from_customer = ""
                self.status = 2
                self.last_status = 1'''

            if self.status == 2:

                # 客户服务agent处理查询
                print("AI思考中...")
                self.back_to_thinking_mode_signal.emit()
                
                customer_service_response = Workflow.api_call_with_retry(
                        self.customer_service_agent.process_query,
                        database_info, 
                        temp_query
                    )                
                # 发送信号
                
                if isinstance(customer_service_response, dict):
                    # 检查所有值是否包含Error
                    has_error = any('rror' in str(value) or 'onnect' in str(value) for value in customer_service_response.values())
                    if has_error:
                        self.status = 0
                        self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                        self.last_status = 2
                        continue
                elif isinstance(customer_service_response, str):
                    if 'rror' in customer_service_response and 'onnect' in customer_service_response:
                        self.status = 0
                        self.last_status = 2
                        self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                        continue
                if ('Y' in customer_service_response["need_clarity"]) and ('稍等' in customer_service_response["to_customer"]):
                    #print(customer_service_response["to_customer"])
                    self.status = 3
                    self.last_status = 2
                    self.message_signal.emit(customer_service_response["to_customer"], False)
                    self.query_from_customer = None
                    self.response_from_dataanalyst = None
                elif ('Y' in customer_service_response["need_clarity"]) and not ('稍等' in customer_service_response["to_customer"]) :
                    self.query_from_customer = "系统提示：检测到客服回答未遵循规则，need_clarity与to_customer中的逻辑相悖，请重新尝试"
                elif ('N' in customer_service_response["need_clarity"]) and ('稍等' in customer_service_response["to_customer"]):
                    self.query_from_customer = "系统提示：检测到客服回答未遵循规则，need_clarity与to_customer中的逻辑相悖，请重新尝试"
                else:
                    #print(customer_service_response["to_customer"])
                    self.message_signal.emit(customer_service_response["to_customer"], False)
                    self.status = 0
                    self.last_status = 2



            if self.status == 3:
                conversation_history = self.customer_service_agent.history
                print("需求分析中...")
                
                task_summary_response = Workflow.api_call_with_retry(
                        self.task_summary_agent.process_query,
                        database_info, 
                        conversation_history
                    )
                if isinstance(task_summary_response, dict):
                    # 检查所有值是否包含Error
                    has_error = any('rror' in str(value) or 'onnect' in str(value) for value in task_summary_response.values())
                    if has_error:
                        self.status = 0
                        self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                        self.last_status = 3
                        continue
                elif isinstance(task_summary_response, str):
                    if 'rror' in task_summary_response and 'onnect' in task_summary_response:
                        self.status = 0
                        self.last_status = 3
                        self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                        continue
                self.status = 4
                self.last_status = 3
            
            if self.status == 4:
                print("尝试取数中...")
                self.operating_mode_signal.emit()
                data_analysis_response = Workflow.api_call_with_retry(
                        self.data_analysis_agent.process_query,
                        database_info, 
                        task_summary_response['task_summary']
                    )
                print(data_analysis_response)
                if isinstance(data_analysis_response, dict):
                    # 检查所有值是否包含Error
                    print(1)
                    has_error = any('rror' in str(value) or 'onnect' in str(value) for value in data_analysis_response.values())
                    if has_error:
                        self.status = 0
                        self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                        self.last_status = 4
                        continue
                elif isinstance(data_analysis_response, str):
                    print(2)
                    if 'rror' in data_analysis_response and 'onnect' in data_analysis_response:
                        self.status = 0
                        self.last_status = 4
                        self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                        continue
                print(3)
                feasibility_result = data_analysis_response['feasibility'].strip()
                if 'Y' in feasibility_result:
                    print("数已取好，请查看数据")
                    #print(data_analysis_response['python_code'])  
                    python_code = data_analysis_response.get('python_code')




                    self.status = 5    
                    self.last_status = 4         
                        


                elif 'N' in feasibility_result:
                    print(f"该需求难以实现，请重新尝试")
                    self.status = 0
                    self.last_status = 4
                    self.customer_service_agent.history.append({
                            "role": "数据库前台",
                            "content": f"该需求难以实现，请重新尝试。分析如下：{data_analysis_response['python_code']}"
                        })
                    self.message_signal.emit(f"该需求难以实现，请重新尝试。分析如下：{data_analysis_response['python_code']}", False)

                else:
                    continue


            if self.status == 5:
                
                try:
                    code_to_execute = re.search(r'```python(.*?)```', python_code, re.DOTALL).group(1).strip().lstrip('\n')
                except:
                    python_code = python_code.split('```python')[-1]
                    python_code = python_code.rstrip('```')
                    code_to_execute = python_code

                if code_to_execute:

                    previous_code = code_to_execute
                    self.previous_code_signal.emit(previous_code)
                    codesequence = []
                    self.codesequence_signal.emit(codesequence)
                    
                    print("正在执行取数代码...")
                    exec_namespace = {
                        'pd': pd,
                        'np': np,
                        'sm': sm,
                        'tsa': tsa,
                        
                        'df': self.df.copy() if self.df is not None else None
                    }
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            exec(code_to_execute, exec_namespace)

                        # 检查result_df是否存在
                        if 'result_df' in exec_namespace:
                            result_df = exec_namespace['result_df']
                        else:
                            print("111AI没按规则回答，正在重新规划路径。")
                            self.status = self.last_status
                            self.last_status = 5
                            continue
                        if isinstance(result_df, pd.DataFrame):
                            if result_df.empty:
                                print("生成的DataFrame为空，正在检查问题。")
                                problem = 0#problem = 0代表着为空
                                if self.last_status == 6:
                                    if self.double_check<2:
                                        self.status = 4
                                        self.last_status = 5
                                    else:
                                        
                                        #报告给客户查找不到合适的数据并添加客服记忆
                                        print("没有查找到合适的数据，返回数据集为空，这很可能是由于数据库中没有相关的数据，您可以再次尝试或者问问其他的问题。")
                                        self.customer_service_agent.history.append({
                                            "role": "数据库前台",
                                            "content": f"没有查找到合适的数据，返回数据集为空，这很可能是由于数据库中没有相关的数据，您可以再次尝试或者问问其他的问题。"
                                        })
                                        self.message_signal.emit("没有查找到合适的数据，返回数据集为空，这很可能是由于数据库中没有相关的数据，您可以再次尝试或者问问其他的问题。", False)
                                        self.last_status = 5
                                        self.status = 0
                                        self.double_check = 0
                                else:
                                    self.status = 6
                                    self.last_status = 5
                            else:
                                self.double_check = 0


                                # 发送DataFrame到前端显示
                                self.data_signal.emit(result_df,True)
                                print(result_df)

                                
                                codesequence.append(previous_code)
                                self.codesequence_signal.emit(codesequence)
                                
                                sample_rows = self.df.sample(n=min(5, len(self.df)))
                                sample_text = sample_rows.to_string(index=False)
                                sample_text

                                self.customer_service_agent.history.append({
                                    "role": "数据库前台",
                                    "content": f"数据分析师已经取好数据，前五行数据如下：\n    {sample_text}\n    取数ypthon代码如下：\n{code_to_execute}\n    您可以提出对该数据的修改意见，我们将在弄清您的进一步意向后为您重新提取数据；或者你想详细弄清这些数据是如何计算的，我也可以为您解释；又或者该数据已经满足了您的需求，您可以提出新的需求，我们将move on to your next task"
                                })
                                self.back_to_thinking_mode_signal.emit()
                                customer_service_response = Workflow.api_call_with_retry(
                                        self.customer_service_agent.process_query,
                                        database_info, 
                                        '请您根据代码，简述你们取数或预测的思路与逻辑。'
                                    )                
                                # 发送信号
                                self.message_signal.emit(customer_service_response["to_customer"], False)
                                                

                            
                                self.status = 0
                                self.last_status = 5
                        else:
                            print("未生成有效DataFrame，正在重新规划路径。")
                            self.status = self.last_status
                            self.last_status = 5
                    except Exception as e:
                        error_message = f"代码执行失败: {str(e)}"
                        print(error_message)
                        import traceback
                        traceback.print_exc()
                        problem = 1#problem = 1代表着运行报错
                        if self.last_status == 6:
                            if self.double_check<2:
                                self.status = 4
                                self.last_status = 5
                            else:
                                self.double_check = 0
                                #报告给客户查找失败，AI对您的逻辑没有理解，您可以详细再说说。并添加客服记忆
                                print("AI经多次尝试后依旧报错，这或许是由于AI没能理解清晰您的需求，您可以详细再说说，或者移步其他问题，等AI再进化两年。")
                                self.customer_service_agent.history.append({
                                    "role": "数据库前台",
                                    "content": f"数据分析师经多次尝试后依旧报错，这或许是由于我们没能理解清晰您的需求，您可以详细再说说，或者移步其他问题。"
                                })
                                self.message_signal.emit("数据分析师经多次尝试后依旧报错，这或许是由于我们没能理解清晰您的需求，您可以详细再说说，或者移步其他问题。", False)
                                self.last_status = 5
                                self.status = 0
                        else:
                            self.status = 6
                            self.last_status = 5
                else:
                    print("222AI没按规则回答，正在重新规划路径。")
                    self.status = 4
                    self.last_status = 5


            if self.status == 6:
                if problem == 0:
                    #返回为空
                    problemds = "返回为空"
                    self.back_to_thinking_mode_signal.emit()
                    bugfinder_response = Workflow.api_call_with_retry(
                            self.bugfinder_agent.process_query,
                            database_info, 
                            task_summary_response['task_summary'],
                            problem,
                            problemds, 
                            code_to_execute
                        )

                    if isinstance(bugfinder_response, dict):
                        # 检查所有值是否包含Error
                        has_error = any('rror' in str(value) or 'onnect' in str(value) for value in bugfinder_response.values())
                        if has_error:
                            self.status = 0
                            self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                            self.last_status = 6
                            continue
                    elif isinstance(bugfinder_response, str):
                        if 'rror' in bugfinder_response and 'onnect' in bugfinder_response:
                            self.status = 0
                            self.last_status = 6
                            self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                            continue

                    if "不" in bugfinder_response["diagnose"]:
                        print("没有查找到合适的数据，返回数据集为空，这很可能是由于数据库中没有相关的数据，您可以再次尝试或者问问其他的问题。")
                        self.customer_service_agent.history.append({
                                    "role": "数据库前台（我）",
                                    "content": f"没有查找到合适的数据，返回数据集为空，这很可能是由于数据库中没有相关的数据，您可以再次尝试或者问问其他的问题。"
                                })
                        self.message_signal.emit("没有查找到合适的数据，返回数据集为空，这很可能是由于数据库中没有相关的数据，您可以再次尝试或者问问其他的问题。", False)
                        #告诉客户没有查找到合适的数据 并且添加客服记忆
                        self.status = 0
                        self.last_status = 6
                        self.double_check = 0
                    else:
                        python_code = bugfinder_response['python_code']
                        self.last_status = 6
                        self.status = 5   
                        self.double_check = self.double_check + 1 
        
                        
                else:
                    #运行报错
                    problemds = f"代码执行失败,报错如下: {error_message}"
                    self.back_to_thinking_mode_signal.emit()
                    bugfinder_response = self.api_call_with_retry(
                            self.bugfinder_agent.process_query,
                            database_info, 
                            task_summary_response['task_summary'],
                            problem,
                            problemds, 
                            code_to_execute
                        )
                    if isinstance(bugfinder_response, dict):
                        # 检查所有值是否包含Error
                        has_error = any('rror' in str(value) or 'onnect' in str(value) for value in bugfinder_response.values())
                        if has_error:
                            self.status = 0
                            self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                            self.last_status = 6
                            continue
                    elif isinstance(bugfinder_response, str):
                        if 'rror' in bugfinder_response and 'onnect' in bugfinder_response:
                            self.status = 0
                            self.last_status = 6
                            self.customer_service_agent.history = self.customer_service_agent.history[:-1]
                            continue
                    if "不" in bugfinder_response["diagnose"]:
                        print("没有查找到合适的数据，返回数据集为空，这很可能是由于数据库中没有相关的数据，您可以再次尝试或者问问其他的问题。")
                        self.customer_service_agent.history.append({
                            "role": "数据库前台（我）",
                            "content": f"数据分析师没有查找到合适的数据，返回数据集为空，这很可能是由于数据库中没有相关的数据，您可以再次尝试或者问问其他的问题。"
                        })
                        self.message_signal.emit("数据分析师没有查找到合适的数据，返回数据集为空，这很可能是由于数据库中没有相关的数据，您可以再次尝试或者问问其他的问题。", False)
                        #告诉客户没有查找到合适的数据 并且添加客服记忆
                        self.status = 0
                        self.last_status = 6
                        self.double_check = 0
                    else:
                        python_code = bugfinder_response['python_code']
                        self.last_status = 6
                        self.status = 5   
                        self.double_check = self.double_check + 1 





class AdjustmentThread(QThread):
    def __init__(self, adjustmentworkflow):
        super().__init__()
        self.adjustmentworkflow = adjustmentworkflow
    
    def run(self):
        self.adjustmentworkflow.adjustment_run()

    def stop(self):
        """强制停止线程"""
        self.adjustmentworkflow.running = False
        self.adjustmentworkflow.adjustment_requirement = None
        self.terminate()  # 强制终止线程
        self.wait()      # 等待线程结束



class AdjustmentWorkflow(QObject):
    # 定义信号

    data_signal = pyqtSignal(object, bool)  # 用于发送DataFrame
    conversation_mode_signal = pyqtSignal(bool)  # 新增信号
    success_message_signal = pyqtSignal(str,str)
    error_message_signal = pyqtSignal(str,str)

    previous_code_signal = pyqtSignal(object)
    codesequence_signal = pyqtSignal(object)
 
    operating_mode_signal = pyqtSignal()
    seeking_mode_signal = pyqtSignal()
    database_information_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.adjustment_agent = createAgentsOPENAI.AdjustmentAgent()
        self.adjustment_requirement = None
        self.status = 0
        self.running = True
        self.currentpage = None
        self.database_information = None
        self.codesequence = []
        self.df = None
        self.ds = None
        
    def import_data(self,DF):
        self.df = DF
        self.df.columns = self.df.columns.str.replace(r'[\n\r\t]', '', regex=True)
    def set_ds(self,DS):
        self.ds = DS
    @staticmethod
    def api_call_with_retry(func, *args, **kwargs):
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            response = func(*args, **kwargs)
            
            # 检查返回值是否包含错误信息
            if isinstance(response, dict):
                # 检查所有值是否包含Error
                has_error = any('rror: ' in str(value) or 'onnect' in str(value) for value in response.values())
                if not has_error:
                    return response
            elif isinstance(response, str):
                if 'rror: ' not in response and 'onnect' not in response:
                    return response
                
            retry_count += 1
            if retry_count == max_retries:
                print(f"API调用失败，连续{max_retries}次返回错误")
                return response
            print(f"API返回错误，正在进行第{retry_count}次重试...")
            time.sleep(2)  # 重试前等待2秒

    def clear_memory(self):
        """清理所有状态"""
        self.running = True
        self.adjustment_requirement = None
        self.status = 0
        self.adjustment_agent = createAgentsOPENAI.AdjustmentAgent()
        self.currentpage = None
        self.database_information = None
        self.codesequence = []
        self.df = None
        # 发送重置信号
        self.conversation_mode_signal.emit(True)
        self.previous_code_signal.emit(None)
        self.codesequence_signal.emit([])



    def adjustment_run(self):
        while self.running:
            if self.status == 0:

                while self.adjustment_requirement is None and self.running or self.currentpage is None  or self.codesequence ==[]:
                    time.sleep(0.5)  # 短暂休眠避免CPU占用过高
                time.sleep(0.5)            

                if self.database_information is None :
                    print("AI查看数据库中（RAG）...")

                    self.seeking_mode_signal.emit()

                    database_info = summarize_data(self.df,self.ds,self.adjustment_requirement)
                    self.database_information = database_info
                    self.database_information_signal.emit(database_info)


                self.codesequence = self.codesequence[:self.currentpage+1]
                self.operating_mode_signal.emit()
                adjustment_response = self.api_call_with_retry(
                    self.adjustment_agent.process_query,
                    self.database_information, 
                    self.codesequence[self.currentpage],
                    self.adjustment_requirement
                    )
                self.conversation_mode_signal.emit(True)
                if isinstance(adjustment_response, dict):
                    # 检查所有值是否包含Error
                    has_error = any('rror' in str(value) or 'onnect' in str(value) for value in adjustment_response.values())
                    if has_error:
                        self.status = 0
                        continue
                elif isinstance(adjustment_response, str):
                    if 'rror' in adjustment_response and 'onnect' in adjustment_response:
                        self.status = 0
                        continue
                #还需要检查代码、NY，然后再status = 1
                feasibility_result = adjustment_response['feasibility'].strip()
                if 'Y' in feasibility_result:
                    print("数已取好，请查看数据")
                    #print(data_analysis_response['python_code'])  
                    python_code = adjustment_response.get('python_code')
                    




                    self.status = 1
                    self.last_status = 0         
                        


                elif 'N' in feasibility_result:
                    print(f"AI认为该需求难以实现，若您认为可以实现，请重新尝试")
                    self.status = 0
                    self.last_status = 0

                    self.error_message_signal.emit("请重新尝试",f"""AI认为该需求
                    难以实现，若您
                    认为可以实现，
                    请重新尝试。
                    """)

                else:
                    continue
                self.adjustment_requirement = None
                

            if self.status == 1:

                
                try:
                    code_to_execute = re.search(r'```python(.*?)```', python_code, re.DOTALL).group(1).strip().lstrip('\n')
                except AttributeError:
                    python_code = python_code.split('```python')[-1]
                    python_code = python_code.rstrip('```')
                    code_to_execute = python_code
                if code_to_execute:

                    previous_code = code_to_execute
                    self.previous_code_signal.emit(previous_code)
                    
                    print("正在执行取数代码...")
                    exec_namespace = {
                        'pd': pd,
                        'np': np,
                        'sm': sm,
                        'tsa': tsa,
                        
                        'df': self.df.copy() if self.df is not None else None
                    }
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            exec(code_to_execute, exec_namespace)

                        # 检查result_df是否存在
                        if 'result_df' in exec_namespace:
                            result_df = exec_namespace['result_df']
                        else:
                            print("AI没按规则回答，请重新尝试。")
                            self.status =0
                            self.last_status = 1
                            continue
                        if isinstance(result_df, pd.DataFrame):
                            # 发送DataFrame到前端显示
                            #这边有点麻烦了，需要再修改之前的代码，将run中发送的信号设置为重新触发resultpreviewpanel，而此处是添加一个新的resultpreviewpanel页面
                            self.data_signal.emit(result_df,False)
                            print(result_df)

                            

                            self.codesequence.append(previous_code)
                            self.codesequence_signal.emit(self.codesequence)
                            
                            


       
                            # 发送信号
                            self.success_message_signal.emit("微调成功",f"""
                            ←-请查看数据
                            若有进一步的
                            需求，请继续
                            调整表格。
                            """)
                                                
                            self.status = 0
                            self.last_status = 1
                        else:
                            print("未生成有效DataFrame，请重新尝试。")
                            self.status = 0
                            self.last_status = 1
                    except Exception as e:
                        error_message = f"""
                        这可能是因为
                        AI还不够智能
                        请重新尝试
                        """
                        self.error_message_signal.emit("执行出错",error_message)
                        print(error_message)
                        import traceback
                        traceback.print_exc()
                        self.status = 0
                        self.last_status = 1

                else:
                    print("AI没按规则回答，请重新尝试。")
                    self.status = 0
                    self.last_status = 1



                

class DrawThread(QThread):
    def __init__(self, drawworkflow):
        super().__init__()
        self.drawworkflow = drawworkflow
    
    def run(self):
        """启动绘图工作流"""
        self.drawworkflow.draw_run()

    def stop(self):
        """强制停止线程"""
        self.drawworkflow.running = False
        self.drawworkflow.drawing_request = None
        self.terminate()  # 强制终止线程
        self.wait()       # 等待线程结束

class DrawWorkflow(QObject):
    # 定义信号

    image_signal = pyqtSignal(object)  

    conversation_mode_signal = pyqtSignal(bool)  
    success_message_signal = pyqtSignal(str,str)
    error_message_signal = pyqtSignal(str,str)
    drawing_codesequence_signal = pyqtSignal(object)
    result_database_info_signal = pyqtSignal(object)
    seeking_mode_signal = pyqtSignal()  
    operating_mode_signal = pyqtSignal()



    
    def __init__(self):
        super().__init__()
        self.draw_agent = createAgentsOPENAI.DrawAgent()
        self.drawing_request = None
        self.status = 0
        self.running = True
        self.result_database_info = None
        """在前端点击绘图按钮后，我们再启动result_database_info的函数，并且由前端传入后端。每次点击绘图按钮都要调用并传入一次
        而若是点击绘图的微调按钮，则不用重新调用result_database_info的函数，直接使用已有的databaseinfo即可。"""
        self.drawing_codesequence = []
        self.df = None
        self.ds = ""
        
        
    def import_data(self,DF):
        self.df = DF
        self.df.columns = self.df.columns.str.replace(r'[\n\r\t]', '', regex=True)

    @staticmethod
    def api_call_with_retry(func, *args, **kwargs):
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            response = func(*args, **kwargs)
            
            # 检查返回值是否包含错误信息
            if isinstance(response, dict):
                # 检查所有值是否包含Error
                has_error = any('rror: ' in str(value) or 'onnect' in str(value) for value in response.values())
                if not has_error:
                    return response
            elif isinstance(response, str):
                if 'rror: ' not in response and 'onnect' not in response:
                    return response
                
            retry_count += 1
            if retry_count == max_retries:
                print(f"API调用失败，连续{max_retries}次返回错误")
                return response
            print(f"API返回错误，正在进行第{retry_count}次重试...")
            time.sleep(2)  # 重试前等待2秒

    def clear_memory(self):
        """清理所有状态"""
        self.running = True
        self.drawing_request = None
        self.status = 0
        self.draw_agent = createAgentsOPENAI.DrawAgent()
        self.result_database_info = None
        self.drawing_codesequence = []
        self.df = None
        # 发送重置信号
        self.conversation_mode_signal.emit(True)
        self.drawing_codesequence_signal.emit([])


        self.result_database_info_signal.emit(self.result_database_info)


    def draw_run(self):
        while self.running:
            if self.status == 0:

                self.df = None
                self.drawing_request = None
                self.drawing_codesequence = []
                #前端需要发送df和drawing_request
                while self.drawing_request is None or self.df is None:
                    time.sleep(0.5)  # 短暂休眠避免CPU占用过高
                temp_query = self.drawing_request
                print(temp_query)
                print(self.df)
                print("AI查看数据中（rag）...")

                self.seeking_mode_signal.emit()

                self.result_database_info = summarize_data(self.df,self.ds,temp_query)
                self.result_database_info_signal.emit(self.result_database_info)
                
                self.operating_mode_signal.emit()
                draw_response = self.api_call_with_retry(
                    self.draw_agent.process_query,
                    self.result_database_info, 
                    self.drawing_request
                    )
                self.conversation_mode_signal.emit(True)
                if isinstance(draw_response, dict):
                    # 检查所有值是否包含Error
                    has_error = any('rror' in str(value) or 'onnect' in str(value) for value in draw_response.values())
                    if has_error:
                        self.status = 0
                        continue
                elif isinstance(draw_response, str):
                    if 'rror' in draw_response and 'onnect' in draw_response:
                        self.status = 0
                        continue
                #还需要检查代码、NY，然后再status = 1
                
  
                python_code = draw_response.get('python_code')
                    




                self.status = 1
                self.last_status = 0         
                        


                
                

            if self.status == 1:

                
                try:
                    code_to_execute = re.search(r'```python(.*?)```', python_code, re.DOTALL).group(1).strip().lstrip('\n')
                except AttributeError:
                    python_code = python_code.split('```python')[-1]
                    python_code = python_code.rstrip('```')
                    code_to_execute = python_code
                if code_to_execute:

                    previous_code = code_to_execute

                    
                    print("正在执行取数代码...")
                    exec_namespace = {
                        'pd': pd,
                        'np': np,
                        'plt': plt,
                        'io.BytesIO': io.BytesIO,
                        'BytesIO': BytesIO,

                        'df': self.df.copy() if self.df is not None else None
                    }
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            exec(code_to_execute, exec_namespace)

                        # 检查result_df是否存在
                        if 'plot_data' in exec_namespace:
                            plot_data = exec_namespace['plot_data']
                        else:
                            print("AI没按规则回答，请重新尝试。")
                            self.status =0
                            self.last_status = 1
                            continue
                        if isinstance(plot_data, BytesIO):
                            self.image_signal.emit(plot_data)

                            print("图表生成成功")

                            

                            self.drawing_codesequence.append(previous_code)
                            self.drawing_codesequence_signal.emit(self.drawing_codesequence)
                            print(previous_code)
                            print(self.drawing_codesequence)
                            
                            


       
                            # 发送信号
                            self.success_message_signal.emit("绘制成功",f"""
                            请查看图表-→
                            若要进一步调
                            整该图，请在
                            右侧面板输入
                            调整需求。
                            """)
                                                
                            self.status = 0
                            self.last_status = 1
                        else:
                            print("未生成有效plot，请重新尝试。")
                            self.status = 0
                            self.last_status = 1
                    except Exception as e:
                        error_message = f"""
                        这可能是因为
                        AI还不够智能
                        请重新尝试
                        """
                        self.error_message_signal.emit("执行出错",error_message)
                        print(error_message)
                        import traceback
                        traceback.print_exc()
                        self.status = 0
                        self.last_status = 1

                else:
                    print("AI没按规则回答，请重新尝试。")
                    self.status = 0
                    self.last_status = 1



                

"""还得做一个绘图微调的agent，需要记录对话序列、从drawingcodesequence中取出代码、以及current_plot数字页码"""


class DrawAdjustmentThread(QThread):
    def __init__(self, draw_adjustment_workflow):
        super().__init__()
        self.draw_adjustment_workflow = draw_adjustment_workflow
    
    def run(self):
        """启动绘图微调工作流"""
        self.draw_adjustment_workflow.draw_run()

    def stop(self):
        """强制停止线程"""
        self.draw_adjustment_workflow.running = False
        self.draw_adjustment_workflow.drawing_request = None
        self.terminate()  # 强制终止线程
        self.wait()       # 等待线程结束

class DrawAdjustmentWorkflow(QObject):
    # 定义信号

    image_signal = pyqtSignal(object)  
    image_sequence_signal = pyqtSignal(object)
    conversation_mode_signal = pyqtSignal(bool)  
    success_message_signal = pyqtSignal(str,str)
    error_message_signal = pyqtSignal(str,str)
    drawing_codesequence_signal = pyqtSignal(object)

    operating_mode_signal = pyqtSignal()



    
    def __init__(self):
        super().__init__()
        self.draw_adjustment_agent = createAgentsOPENAI.DrawAdjustmentAgent()
        self.drawing_request = None
        self.status = 0
        self.running = True
        self.result_database_info = None
        """在前端点击绘图按钮后，我们再启动result_database_info的函数，并且由前端传入后端。每次点击绘图按钮都要调用并传入一次
        而若是点击绘图的微调按钮，则不用重新调用result_database_info的函数，直接使用已有的databaseinfo即可。"""
        self.drawing_codesequence = []
        self.df = None
        self.result_database_info = None
        self.last_code = None
        self.current_plot = None
        self.image_sequence = []


        
        
    def import_data(self,DF):
        self.df = DF
        self.df.columns = self.df.columns.str.replace(r'[\n\r\t]', '', regex=True)

    @staticmethod
    def api_call_with_retry(func, *args, **kwargs):
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            response = func(*args, **kwargs)
            
            # 检查返回值是否包含错误信息
            if isinstance(response, dict):
                # 检查所有值是否包含Error
                has_error = any('rror: ' in str(value) or 'onnect' in str(value) for value in response.values())
                if not has_error:
                    return response
            elif isinstance(response, str):
                if 'rror: ' not in response and 'onnect' not in response:
                    return response
                
            retry_count += 1
            if retry_count == max_retries:
                print(f"API调用失败，连续{max_retries}次返回错误")
                return response
            print(f"API返回错误，正在进行第{retry_count}次重试...")
            time.sleep(2)  # 重试前等待2秒

    def clear_memory(self):
        """清理所有状态"""
        self.running = True
        self.drawing_request = None
        self.status = 0
        self.draw_adjustment_agent = createAgentsOPENAI.DrawAdjustmentAgent()
        self.result_database_info = None
        self.drawing_codesequence = []
        self.df = None
        self.image_sequence = []
        # 发送重置信号
        self.conversation_mode_signal.emit(True)
        self.drawing_codesequence_signal.emit([])



        self.last_code = None
        self.current_plot = None
        self.image_sequence_signal.emit(self.image_sequence)


    def draw_run(self):
        while self.running:
            if self.status == 0:
                print("正在等待调整需求")
                print(self.drawing_request)
                print(self.drawing_codesequence)
                print(self.df)
                print(self.result_database_info)
                self.df = None
                self.drawing_request = None
                self.drawing_codesequence = []
                self.result_database_info = None
                self.last_code = None
                self.current_plot = None
                self.image_sequence = []
                #前端需要发送df和drawing_request
                while self.drawing_request is None or self.df is None or self.result_database_info is None or self.drawing_codesequence ==[] or self.current_plot is None or self.image_sequence == []:
                    time.sleep(0.5)  # 短暂休眠避免CPU占用过高:

                temp_query = self.drawing_request
                print(temp_query)
                print(self.df)


                

                self.last_code = self.drawing_codesequence[self.current_plot]
                self.operating_mode_signal.emit()
                draw_response = self.api_call_with_retry(
                    self.draw_adjustment_agent.process_query,
                    self.result_database_info, 
                    self.drawing_request,
                    self.last_code
                    )
                print(draw_response)
                self.conversation_mode_signal.emit(True)
                if isinstance(draw_response, dict):
                    # 检查所有值是否包含Error
                    has_error = any('rror' in str(value) or 'onnect' in str(value) for value in draw_response.values())
                    if has_error:
                        self.status = 0
                        continue
                elif isinstance(draw_response, str):
                    if 'rror' in draw_response and 'onnect' in draw_response:
                        self.status = 0
                        continue
                #还需要检查代码、NY，然后再status = 1
                
  
                python_code = draw_response.get('python_code')
                    




                self.status = 1
                self.last_status = 0         
                        


                
                

            if self.status == 1:

                
                try:
                    code_to_execute = re.search(r'```python(.*?)```', python_code, re.DOTALL).group(1).strip().lstrip('\n')
                except AttributeError:
                    python_code = python_code.split('```python')[-1]
                    python_code = python_code.rstrip('```')
                    code_to_execute = python_code
                if code_to_execute:

                    previous_code = code_to_execute

                    
                    print("正在执行取数代码...")
                    exec_namespace = {
                        'pd': pd,
                        'np': np,
                        'plt': plt,
                        'io.BytesIO': io.BytesIO,
                        'BytesIO': BytesIO,

                        'df': self.df.copy() if self.df is not None else None
                    }
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            exec(code_to_execute, exec_namespace)

                        # 检查result_df是否存在
                        if 'plot_data' in exec_namespace:
                            plot_data = exec_namespace['plot_data']
                        else:
                            print("AI没按规则回答，请重新尝试。")
                            self.status =0
                            self.last_status = 1
                            continue
                        if isinstance(plot_data, BytesIO):
                            self.image_signal.emit(plot_data)

                            print("图表生成成功")

                            
                            self.drawing_codesequence = self.drawing_codesequence[:self.current_plot+1]
                            self.drawing_codesequence.append(previous_code)
                            self.drawing_codesequence_signal.emit(self.drawing_codesequence)

                            self.image_sequence = self.image_sequence[:self.current_plot+1]
                            self.image_sequence.append(plot_data)
                            self.image_sequence_signal.emit(self.image_sequence)
                            
                            


       
                            # 发送信号
                            self.success_message_signal.emit("绘制成功",f"""
                            请查看图表-→
                            若要进一步调
                            整该图，请在
                            右侧面板输入
                            调整需求。
                            """)
                                                
                            self.status = 0
                            self.last_status = 1
                        else:
                            print("未生成有效plot，请重新尝试。")
                            self.status = 0
                            self.last_status = 1
                    except Exception as e:
                        error_message = f"""
                        这可能是因为
                        AI还不够智能
                        请重新尝试
                        """
                        self.error_message_signal.emit("执行出错",error_message)
                        print(error_message)
                        import traceback
                        traceback.print_exc()
                        self.status = 0
                        self.last_status = 1

                else:
                    print("AI没按规则回答，请重新尝试。")
                    self.status = 0
                    self.last_status = 1
