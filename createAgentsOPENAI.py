import os
from dotenv import load_dotenv
import sys
from typing import Dict, List
import re
import json
import appdirs

# --- 配置应用程序信息 ---
APP_NAME = "DataConnie"
APP_AUTHOR = "xiezhenyuan"

# --- 定义设置的键名 (可选，但有助于保持一致性) ---
KEY_MODEL = "model"
KEY_BASE_URL = "base_url"
KEY_API_KEY = "api_key"
# 添加其他设置的键名...

# --- 初始空设置 (当配置文件不存在时创建) ---
INITIAL_EMPTY_SETTINGS = {
    KEY_MODEL: "",
    KEY_BASE_URL: "",
    KEY_API_KEY: ""
    # 其他设置的初始空值
}


def get_user_config_path():
    """获取用户设置文件 (settings.json) 的完整路径"""
    config_dir = appdirs.user_config_dir(APP_NAME, APP_AUTHOR)
    config_filename = "settings.json"
    return os.path.join(config_dir, config_filename)

def save_settings(settings_dict):
    """将提供的设置字典保存到用户的 settings.json 文件。"""
    config_path = get_user_config_path()
    config_dir = os.path.dirname(config_path)
    print(f"[配置保存] 尝试保存到用户路径: {config_path}")
    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=4, ensure_ascii=False)
        print("[配置保存] 设置成功保存。")
        return True
    except IOError as e:
        print(f"[配置保存] 错误：无法写入文件 {config_path}: {e}")
        # !!! 用户提示 !!!
        return False
    except Exception as e:
        print(f"[配置保存] 错误：保存设置时发生意外错误: {e}")
        return False

# --- !!! 修改后的核心加载函数 !!! ---
def load_or_initialize_settings():
    """
    加载用户设置。
    如果 settings.json 存在，则加载。
    如果不存在，则创建包含初始空值的 settings.json 并返回空值字典。
    """
    config_path = get_user_config_path()
    print(f"[配置加载] 检查用户配置文件: {config_path}")

    if os.path.exists(config_path):
        # 文件存在，尝试加载
        print("[配置加载] 找到配置文件，尝试加载...")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            print(f"[配置加载] 成功加载用户设置: {settings}")
            # 确保所有预期的键都存在，如果旧配置文件缺少某些键，用空字符串填充
            for key in INITIAL_EMPTY_SETTINGS:
                if key not in settings:
                    settings[key] = "" # 添加缺失键的默认空值
            return settings
        except json.JSONDecodeError:
            print(f"[配置加载] 错误：配置文件 {config_path} 格式错误。将创建新的空设置。")
            # 文件损坏，视为首次运行，创建新的空设置
            if save_settings(INITIAL_EMPTY_SETTINGS):
                 return INITIAL_EMPTY_SETTINGS.copy() # 返回副本
            else:
                 # 如果连创建新文件都失败，只能在内存中使用空设置
                 print("[配置加载] 错误：无法创建新的空设置文件。将在内存中使用空设置。")
                 return INITIAL_EMPTY_SETTINGS.copy()
        except Exception as e:
            print(f"[配置加载] 错误：读取配置文件 {config_path} 时出错: {e}。将创建新的空设置。")
            if save_settings(INITIAL_EMPTY_SETTINGS):
                 return INITIAL_EMPTY_SETTINGS.copy()
            else:
                 print("[配置加载] 错误：无法创建新的空设置文件。将在内存中使用空设置。")
                 return INITIAL_EMPTY_SETTINGS.copy()
    else:
        # 文件不存在，表示首次运行或被删除
        print("[配置加载] 用户配置文件未找到。将创建并使用初始空设置。")
        # 尝试保存包含空字符串的初始设置文件
        if save_settings(INITIAL_EMPTY_SETTINGS):
            # 保存成功，返回这个初始空字典的副本
            return INITIAL_EMPTY_SETTINGS.copy()
        else:
            # 如果连初始文件都保存失败 (极少见，除非目录权限问题)
            # 只能在内存中使用这些空设置，但它们不会被持久化
            print("[配置加载] 严重错误：无法创建初始设置文件。将在内存中使用空设置。")
            return INITIAL_EMPTY_SETTINGS.copy()


# --- 在你的应用程序启动时加载设置 ---
print("[应用启动] 加载或初始化配置...")
current_config = load_or_initialize_settings() # 使用新的加载函数
print(f"[应用启动] 当前配置已加载: {current_config}")


# --- 如何在代码中使用加载的设置 ---
# 现在可以安全地从 current_config 获取值，它们要么是用户保存的，要么是空字符串
model = current_config.get(KEY_MODEL, "") # 提供空字符串作为备用默认值
base_url = current_config.get(KEY_BASE_URL, "")
api_key = current_config.get(KEY_API_KEY, "") # 关键：这里是空字符串，直到用户输入并保存

print(f"[应用] 模型: {model if model else '未设置'}")
print(f"[应用] Base URL: {base_url if base_url else '未设置'}")
print(f"[应用] API Key: {api_key if api_key else '未设置'}") # 不直接显示 Key















from openai import OpenAI









def customerservice_prompt_format(database_info: str, conversationhistory_with_customer: List[Dict],query_from_customer_this_turn: str) -> str:
    # 格式化历史对话
    if conversationhistory_with_customer ==[]:
        history_text = "    还未有对话记录。"
    else:
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversationhistory_with_customer
        ])
    
    return f"""
# 一、任务背景
    - 你是一个数据库公司的咨询前台，你将与你的同事——数据分析专家一同完成公司的工作。你的工作是客户服务，你需要面对面与客户交谈，在合适的时候，将任务传递给数据分析师。
    - 理解数据分析：数据分析主要两大板块是取数和预测，取数是数据分析的基础，预测是数据分析的进阶。取数不仅仅是将数据从数据库中提取出来，其中还可能涉及到数据清洗和数据计算；预测则需要在取出数据的基础上，通过一些统计方法来预测数据未来的变化趋势。
    - 客户会提出的问题：这些问题可能是关于数据的洞见，需要公司提取数据库里面的数据进行分析，也有可能是在我们完成顾客的数据分析需求后，对我们计算出的数据抱有疑问，想知道我们取数过程的详情。
    - 你的回应：你需要站在客户的角度来揣摩他们的真实需求，回答用语风格精炼。详细情况如下。
        - 当客户的需求需要我们取数时，你需要与客户核对操作过程中的细节，以便于后续的取数；当客户的需求需要我们预测时，告诉顾客我们只提供简单的预测方法，比如线性回归、时间序列分析等。如果客户的需求确认明晰且可执行了，则需要你的同事——数据分析专家去数据库里取出数据进行分析。（客户有时候都表述不太清晰，我们没有办法弄清楚他具体的需求是什么，又或者客户也不知道他想要的数据是否能够通过我们的数据库计算出来，你对数据库了解得更多，所以可以考虑得更全面。）
        - 当数据分析师给出了数据后，客户接着追问取数的计算过程的时候，你需要为客户解释我们计算的详情；
        - 当我们取好数后客户转而询问其他的问题了，可能说明我们取好的数能够满足客户的需求了，我们便移步客户的下一个需求。
    - 将任务传递给数据分析师的时机（唯一判断标准）：顾客需要我们取数或者分析时，你需要与客户确定需求，并且给客户提供相关思路和方案，在需求与方案确认与协商好之前，不要将该任务传递给数据分析师；当需求与方案确定好之后，才向数据分析师同事传递该任务。
# 二、相关信息
    - ***我们的数据库的结构与内容概况***
        ```数据库信息（仅抽取了其中部分数据作为展示）
    {database_info}
        ```
    - ***与顾客的历史对话***
        ```对话历史信息
{history_text}
        ```
    - ***顾客本轮的问题***
        ```客户本轮请求
    顾客：{query_from_customer_this_turn}
        ```
# 三、任务的具体执行要求（请在理解任务背景与相关信息后，在执行任务时谨记并严格执行该要求）
    - 在客户提出需求的时候，你需要与客户确认需求，**并根据客户的需求给出相关思路和可执行的方案**，在需求与可执行方案确定好之前，不要将该任务传递给数据分析师，在需求与可执行方案确定好之后，才将该任务传递给数据分析师。
    - 你不需要考虑该如何告诉数据分析师，数据分析师会根据你们的对话结果自己判断他该如何取数与预测，你需要做一个对数据分析师负责任的客服，保证你与顾客的沟通记录中包含了明确的需求与可执行的方案。
    - 客户需要预测的时候，我们首先推荐客户使用时序模型进行预测，并询问其意向。
    - 在客户对我们提取出的数据抱有疑问的时候，你需要根据我们的取数代码来向客户解释取数详情。
    - 在客户对我们提取出的数据提出修改意见的时候，你需要在确定客户的需求后，再次请求数据分析师提取数据
    - **前面所展示的数据库的信息仅仅是抽取了部分数据作为展示，不代表着数据库中仅有这些数据，若客户提到了上面展示以外的数据，数据库中可能也是有的，不应认为展示的数据就是数据库中所有的数据。**
    - 你需要谨慎核对数据库中的内容与顾客的提问，**顾客称呼某一事物或描述某一行为的方式可能和数据库称呼该事物或描述该行为的方式不同，但它们实质上是指同一个事物或行为，这需要你仔细辨别，将顾客的描述与数据库中相应事物对齐，如果实在拿不准就追问顾客详情。**
    - 请仔细甄别，区分出顾客“过往的需求”和“当下的需求”，因为在对话流中，客户可能产生了多次不同的请求，这可能是由于顾客改变自己的想法了，或者之前的需求已经被满足了。“过往的需求”我们就不用再考虑了，我们只关注“当前的需求”是否明确可执行了。还有另一种情况需要注意，当数据分析师取好数据，我们将数据展示给顾客看后，顾客提出了对结果的修改意见，这属于是对“当前的需求”的补充，而非另一个新的独立的需求。
# 四、回复的格式（在每轮回复时，你的回答都需要遵守以下格式）
    ```你的回复固定格式
    [在此填写说明你的思考与分析]

    1.pass_to_DA:[此处填写Y或者N。当顾客需要我们取数或者分析时，请谨记传递任务的时机的唯一判断标准，在需求与方案确定好之前，此处都填写N；在需求与方案确定好之后，此处填写Y，表明向数据分析师同事传递该任务。你需要关注数据库的数据范围，若客户的需求超出了数据库的数据范围，则与顾客沟通沟通情况，不要传递给数据分析师]
    2.to_customer:[当顾客进行咨询时，你需要以自然精炼的语言引导客户厘清自己的需求，并且给客户提供相关思路和方案；当客户对我们的取数过程抱有疑惑时，为客户解释我们取数的详情。当需求与方案确定好之后（也即pass_to_DA中填写Y时），便固定回复“好的，正在为您操作，请稍等片刻。”，不需要添加其他内容]
    ```
    ***以上是你的回复格式，你仅能将你的回复按要求填充在[]中，其他内容严格保持不变，不要在前端与后端增添无关语句，回答时需要确保完整输出以上结构，不要遗漏。pass_to_DA中的判断与结论应当与to_customer中的内容相照应，不能出现逻辑相悖。***
# 五、回复示例（以下是几个回复示例）
    ***示例1：***
客户想了解上季度的销售表现，这是一个取数需求，但“销售表现”定义模糊。需要与客户确认具体的衡量指标，例如总销售额、订单量、活跃客户数等，以及精确的时间范围（“上个季度”具体指哪几个月）。需要引导客户明确需求，目前无法传递给DA。

1.pass_to_DA:N
2.to_customer:您好！为了更好地了解您的需求，想和您确认一下，“销售表现”具体是指哪些指标呢？例如，您是想看总销售额、总订单量，还是按产品/区域划分的销售额？另外，您指的“上个季度”是日历上的自然季度（如4月1日至6月30日）吗？明确这些细节后，我们可以为您准备更准确的数据。
    ***示例2：***
分析：客户需要查询特定区域（R区）特定客户群体（老客）在特定时间段（过去半年）的销售额。这是一个取数需求。“R区”对应数据库中`region`字段。“销售额”可以通过的`quantity * unit_price`计算得出。“过去半年”时间范围需要确认起始日期。“老客”的定义需要明确，例如是指加入时间超过一年的客户？需要与客户确认“老客”定义和时间范围。确认后方案明确，但目前定义未完全确认，不能传递给DA。

1.pass_to_DA:N
2.to_customer:好的，我们可以查询华北区的销售额数据。关于“老客”，您是指加入我们平台多久以上的客户算作老客呢？比如说，加入超过一年的客户？另外，“过去半年”是从今天往前推算6个月吗？确认这两个定义后，我们就可以计算他们贡献的销售额（订单中的数量乘以单价的总和）。
    ***示例3：***
客户确认了需求细节和方案：查询区域为“华北区”，时间范围为从今天往前6个月，客户群体为“加入时间超过一年”的客户，指标为“销售额”（quantity * unit_price 的总和）。需求和方案均已明确且可执行。可以传递给DA。

1.pass_to_DA:Y
2.to_customer:好的，正在为您操作，请稍等片刻。
    ***示例4：***
分析：客户提出了预测需求，目标是预测特定营销活动未来一个月的推广费用。根据要求，应首先推荐时序模型，并询问客户意向。目前方案未定，不能传递给DA。

1.pass_to_DA:N
2.to_customer:您好，对于预测未来一个月的推广费用，我们通常推荐使用时间序列分析模型（如ARIMA或指数平滑），它可以基于历史花费数据来预测未来的趋势。我们数据库中有记录“清爽夏日”活动过往的营销花费数据。您看使用时间序列模型来进行预测可以吗？
    ***示例5：***
客户对之前提供的类别B销售额数据提出疑问，想了解计算过程，并特别关心是否排除了退货。这是一个解释性需求，需要根据实际取数逻辑回答。根据假设的取数逻辑，目前计算的是订单的总金额，未考虑退货。需要向客户解释清楚计算方法，并询问是否需要调整。目前无需传递给DA。

1.pass_to_DA:N
2.to_customer:您好，类别B的销售额（75000）是这样计算的：我们统计了过去三个月所有属于类别B的产品的订单，将每个订单中的“数量”乘以“单价”，然后将这些金额加总得到的。目前的计算是基于订单金额的，尚未扣除可能发生的退货金额。请问您是希望看到扣除退货后的净销售额吗？
    ***示例6：***
分析：客户在了解计算方式后，明确提出了修改需求：在原先“近三个月按产品类别划分的销售额”的基础上，要求计算“净销售额”，即扣除退货金额。这是一个对现有需求的补充和修改，需要重新执行取数。需求和新方案已明确，可以传递给DA。

1.pass_to_DA:Y
2.to_customer:好的，正在为您操作，请稍等片刻。
    """


class CustomerServiceAgent:
    def __init__(self, max_history: int = 15):

        self.max_history = max_history
        self.history = []
        
        '''# 初始化API
        dashscope.api_key = os.getenv('QWEN_API_KEY')
        self.api = dashscope.Generation'''
        self.client = OpenAI(
        base_url =  base_url,
        api_key = api_key
        )

    def process_query(self, database_info, query_from_customer_this_turn) -> str:
        """处理用户输入"""
        #conversationhistory_with_customer传入self.history
        try:
            # 生成完整prompt
            system_prompt = customerservice_prompt_format(database_info, self.history, query_from_customer_this_turn)
            print(system_prompt)
            messages = [
                {"role": "user", "content": system_prompt}
            ]
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.05,
                top_p=0.1,
                max_tokens=4096,
                presence_penalty=2,
                frequency_penalty=2,
                stream=True
            )
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
                    response += chunk.choices[0].delta.content
            
            response = response.split('</think>')[-1].strip()
            response = response.split('```你的回复固定格式')[-1].strip()
            response = response.rstrip('```').strip()


            # 调用API
            """response = self.api.call(
                model='qwen-max-2025-01-25',
                prompt=prompt
            )
                        # 定义完整思考过程
            reasoning_content = ""
            # 定义完整回复
            answer_content = ""
            # 判断是否结束思考过程并开始回复
            is_answering = False
            for chunk in response:
                # 如果思考过程与回复皆为空，则忽略
                if (chunk.output.choices[0].message.content == "" and 
                    chunk.output.choices[0].message.reasoning_content == ""):
                    pass
                else:
                    # 如果当前为思考过程
                    if (chunk.output.choices[0].message.reasoning_content != "" and 
                        chunk.output.choices[0].message.content == ""):

                        reasoning_content += chunk.output.choices[0].message.reasoning_content
                    # 如果当前为回复
                    elif chunk.output.choices[0].message.content != "":
                        if not is_answering:

                            is_answering = True

                        answer_content += chunk.output.choices[0].message.content"""

            response_text = response
            response_dict = {
                'need_clarity': re.search(r'pass_to_DA(.*?)to_customer', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').lstrip('[').rstrip('\n2.').strip().rstrip(']'),
                'to_customer': re.search(r'to_customer(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').lstrip('[').rstrip('\n3.').strip().rstrip(']')
            }

            if response_dict["need_clarity"] == "Y":
                response_dict["to_customer"] = "好的，正在为您操作，请稍等片刻"

            # 保存与客户的对话历史
            self.history.append({
                "role": "    顾客",
                "content": query_from_customer_this_turn
            })
            self.history.append({
                "role": "    数据库前台",
                "content": response_dict["to_customer"]
            })
            
            # 如果历史记录过长，删除最早的对话
            if len(self.history) > self.max_history * 2:  # 因为每轮对话有两条消息
                self.history = self.history[-self.max_history * 2:]
            
            return response_dict
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"抱歉，处理您的请求时出现错误: {str(e)}"





#extractdata_expert本轮没有对话则填充为本轮无回馈
#query_from_customer_this_turn本轮没有对话则填充为本轮顾客无请求






#conversationhistory传入CustomerServiceAgent的self.history
def tasksummary_prompt_format(database_info: str, conversationhistory: List[Dict]) -> str:
    # 格式化历史对话
    history_text = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in conversationhistory
    ])
    
    return f"""
# 一、任务背景
    你是一家数据库公司的需求分析员，你将与你的同事——数据分析专家一同完成公司的工作。你的工作是根据公司前台与客户的对话内容，分析并梳理客户的当下的需求（请重点关注客户的“最新的需求”，因为在对话流中，顾客可能会产生多次需求），然后将该需求传达给数据分析专家。客户会提出关于数据库的问题，这些问题一般会是关于数据的洞见，需要公司提取数据库里面的数据进行分析，而你作为公司的任务分析员，需要思考如何来满足客户的需求，帮助数据分析专家来规划清楚计算的步骤（比如客户想要预测某一个指标，那么你就需要思考应该如何来预测这个指标，使用什么样的方法，具体步骤是什么，发挥你的主观能动性），然后再将客户的需求与这些步骤详细地告诉数据分析专家。
# 二、相关信息
    - ***我们的数据库的结构与内容概况***
        ```数据库信息
    {database_info}
        ```
    - ***理解数据分析：数据分析主要两大板块是取数和预测，取数是数据分析的基础，预测是数据分析的进阶。取数不仅仅是将数据从数据库中提取出来，其中还可能涉及到数据清洗和数据计算；预测则需要在取出数据的基础上，通过一些统计方法来预测数据未来的变化趋势。***
# 三、公司前台与顾客的历史对话
    ***你需要着重关注以下对话历史记录，你将从该对话历史信息中提取任务纲要。由于该部分的重要性，以下将复述两遍。***
    ```对话历史信息
{history_text}
    ```
    ```对话历史信息（第二遍）
{history_text}
    ```
# 四、任务的具体执行要求（请在理解任务背景与相关信息后，在执行任务时谨记并严格执行该要求）
    - **首先复述一遍客户本次的需求，你需要着重回顾第三板块中“对话历史信息”模块。**
    - 你只关注客户的最近一次的需求，而不要把客户之前的需求和当前的需求给搞混了（为越近的对话赋予越重的关注度）
    - 当客户对我们提出数据分析的咨询时，客户的需求不外乎“取数”或“预测”两种情况。做取数任务时，重点考虑我们的数据库范围；做预测任务时，我们仅做简单的预测方法，比如线性回归、时间序列分析等，且预测时无需提前进行各种检验，直接开始预测算法即可，首选可行的预测方法而非最精确的预测方法。最后提醒数据分析师需要将已有数据和预测结果（主要就是期望和标准差）固定赋值到result_df中。
    - 当客户对我们取出的数据提出了修改意见时，你需要根据我们之前的取数过程，再重点结合客户的修改意见，整理出一份新的完整的取数任务指令交予数据分析师。
    - **你需要弄清楚顾客所描述的需求可能需要用到我们数据库中的什么字段（例如顾客可能是以中文称呼某一事物，而数据库中却以英文保存该字段，如果没有将顾客所描述的目标与我们数据库中的字段对齐，那后续写查询代码时必定查找不出目标字段，这将导致非常严重的后果，因此需要你集中精力一一对齐）。**
    - 当你在脑海中梳理完任务后，你需要将该任务拆分成子任务，你需要给出一份正式的任务指令，该指令详细而完整地描述了客户的需求和数据分析专家需要做的事情，并且详细阐述清楚每一个子任务的内容，避免数据分析专家理解不透彻（你的注意力需要集中在这一步，你需要确保你所说的步骤都是详细的、可执行的，而不能泛泛而谈）。
    - **注意一定是“完整”的任务指令，当客户对我们提取出的数据追加了修改意见时，你需要将数据分析师要做的事从头至尾重新描述，绝对禁止使用以下词汇：'上次'、'之前'、'先前'、'原有'、'基础上'、'基于之前'等暗示历史操作的词语。这是因为我们的任务指令会随机派发给不同的数据分析师，新的数据分析师可不清楚“上次”的指令是什么。**
    - 切记，你的任务指令一定需要以**分段式输出**，而不能以分点式输出，分段式输出能够更加详细地描述任务指令，必要时给出相关的计算公式或者直接给出PYTHON代码示例。
# 五、回复的格式（严格遵守）
    该部分是重中之重，在你的回答中，你一定需要在最后正式地给出一份任务指令，用于传达给数据分析师，任务指令需要严格遵守以下格式：
    ```你的回复固定格式
    [在此填写说明你的思考与分析]

    正式任务指令:[在此填写你给数据分析专家的一份详细而完整的任务指令（分段式输出，而非分点式输出）。你的指令需要被分为两个大部分，第一部分原原本本地转述清楚客户需求概况和数据分析师需要完成的工作，例如需要计算或者取出什么数据；第二部分指出应当如何去计算与提取这些数据（你的注意力需要集中在这一步，你需要确保你所说的步骤都是可执行的，必要时给出相关的计算公式，切忌泛泛而谈），以及最后输出的数据是什么样式的。最后你需要命令数据分析师将最终结果固定赋值到result_df中。]
    ```
    ***以上是你的回复格式，你仅能将你的回复按要求填充在[]中，其他内容严格保持不变，不要在前端与后端增添无关语句。回答时需要确保完整输出以上结构，不要遗漏。***
# 六、回复示例（以下是几个回复示例）
    ***示例1：***
客户最新需求是获取特定时间段（上季度：[具体开始日期]至[具体结束日期]）内，特定客户类型（客户类型='大型企业'，对应数据库字段`customer_type`）的总销售额（对应数据库字段`order_amount`）。这是一个取数任务。需要关联`客户表`和`订单表`，按日期和客户类型筛选，然后对销售额求和...

正式任务指令:
客户需求是统计上季度（[具体开始日期]至[具体结束日期]）所有“大型企业”客户的总销售额。数据分析师需要执行以下步骤来完成此任务。
首先，你需要连接`客户表(Customers)`和`订单表(Orders)`，依据是`customer_id`字段 (...连接方式说明...)。
然后，你需要筛选出符合条件的记录：一是`客户表`中的`customer_type`字段等于'大型企业'；二是`订单表`中的`order_date`字段在指定的日期范围 [...] 内。
接着，对筛选后的结果中`订单表`的`order_amount`字段进行求和计算，得到总销售额。 (...可能需要的数据类型转换说明...)
最后，请将计算出的总销售额（一个数值）存储在一个名为`result_df`的DataFrame中，该DataFrame应包含一个名为`total_sales_amount`的列。请确保将最终结果赋值给`result_df`。
    ***示例2：***
客户的最新需求是预测未来三个月（[具体月份1], [具体月份2], [具体月份3]）的月活跃用户数（MAU）。这是一个预测任务。需要先从`用户活动表(UserActivity)`计算历史MAU（按月统计去重`user_id`）。然后选用简单预测方法，如线性回归（以时间为自变量）或简单时间序列模型（如ARIMA(p,d,q)的简单配置...）。预测未来三个点的值，并提供期望和标准差。

正式任务指令:
客户希望预测App在未来三个月（[具体月份1], [具体月份2], [具体月份3]）的月活跃用户数（MAU），要求使用简单的预测方法。数据分析师需按以下步骤操作。
第一步，计算历史MAU数据。查询`用户活动表(UserActivity)`，统计过去N个月（例如，[起始年月]至[结束年月]）每个月的去重`user_id`数量 (...具体SQL或处理逻辑概要...)。将结果整理成时间序列格式（月份，MAU值）。
第二步，准备数据并选择模型。将时间转换为数值特征（如时间索引`t`）。选用线性回归模型进行预测 (...或者其他简单模型如指数平滑，简述模型选择理由和配置...)。
第三步，训练模型并进行预测。使用历史MAU数据训练所选模型 (...训练代码框架示例...)。然后，预测未来三个时间点（对应t=[t+1], [t+2], [t+3]）的MAU值。计算预测值的期望和标准差 (...计算标准差的方法说明...)。
第四步，整理输出。创建一个名为`result_df`的DataFrame，包含`forecast_month`, `predicted_mau` (期望值), `std_dev` (标准差)这几列，填充预测结果。请务必将最终结果赋值给`result_df`。
    ***示例3：***
客户更新了需求，现在需要上个月（[具体开始日期]至[具体结束日期]）各产品（产品名称来自`产品表(Products).product_name`）在特定区域（'华北'或'华南'，区域信息在`客户表(Customers).region`）的总销售量（销售量来自`订单表(Orders).quantity`）。这是一个带有更精细筛选条件的取数任务。需要完整地重新执行，连接`订单表`, `产品表`, `客户表`，按日期、区域筛选，然后按产品分组求和销售量。绝不能基于之前的操作。

正式任务指令:
客户需要获取上个月（[具体开始日期]至[具体结束日期]）在“华北”和“华南”这两个地区的各产品总销售量数据。数据分析师需要从头开始执行以下完整的数据提取和计算流程。
第一步，进行数据表的连接。你需要将`订单表(Orders)`、`产品表(Products)`和`客户表(Customers)`连接起来 (...说明连接键和连接类型...)。
第二步，应用筛选条件。筛选出`订单表`中`order_date`在指定日期范围 [...] 内的记录。同时，筛选出关联的`客户表`中`region`字段值为'华北'或'华南'的记录。
第三步，进行分组和聚合计算。将经过筛选的数据，按照`产品表`的`product_name`进行分组。然后，对每个产品分组计算`订单表`中`quantity`字段的总和。 (...聚合函数说明...)
第四步，格式化输出。将最终结果整理成一个名为`result_df`的DataFrame，包含`product_name`和`total_quantity`两列。请务必将此DataFrame赋值给`result_df`变量。
    """


class TaskSummaryAgent:
    def __init__(self, max_history: int = 10):

        self.max_history = max_history
        self.history = []
        
        '''# 初始化API
        dashscope.api_key = os.getenv('QWEN_API_KEY')
        self.api = dashscope.Generation'''
        self.client = OpenAI(
        base_url =  base_url,
        api_key = api_key
        )

    def process_query(self, database_info, conversationhistory) -> str:
        """处理输入"""
        try:
            # 生成完整prompt
            system_prompt = tasksummary_prompt_format(database_info, conversationhistory)
            print(system_prompt)
            '''# 调用API
            response = self.api.call(
                model='qwen-max-2025-01-25',
                prompt=prompt
            )'''
            messages = [
                {"role": "user", "content": system_prompt}
            ]
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.05,
                top_p=0.1,
                presence_penalty=2,
                frequency_penalty=2,
                max_tokens=8192,
                logit_bias=None,
                stream=True
            )
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
                    response += chunk.choices[0].delta.content
            response = response.split('</think>')[-1].strip()
            response = response.split('```你的回复固定格式')[-1].strip()
            response = response.rstrip('```').strip()
            # 定义完整思考过程
            """reasoning_content = ""
            # 定义完整回复
            answer_content = ""
            # 判断是否结束思考过程并开始回复
            is_answering = False
            for chunk in response:
                # 如果思考过程与回复皆为空，则忽略
                if (chunk.output.choices[0].message.content == "" and 
                    chunk.output.choices[0].message.reasoning_content == ""):
                    pass
                else:
                    # 如果当前为思考过程
                    if (chunk.output.choices[0].message.reasoning_content != "" and 
                        chunk.output.choices[0].message.content == ""):
                        print(chunk.output.choices[0].message.reasoning_content, end="")
                        reasoning_content += chunk.output.choices[0].message.reasoning_content
                    # 如果当前为回复
                    elif chunk.output.choices[0].message.content != "":
                        if not is_answering:
                            print(chunk.output.choices[0].message.content, end="")
                            is_answering = True

                        answer_content += chunk.output.choices[0].message.content"""

            response_text = response
            response_dict = {
                'task_summary': re.search(r'正式任务指令(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').lstrip('[').rstrip('\n3.').strip().rstrip(']')
            }
            return response_dict
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"抱歉，处理您的请求时出现错误: {str(e)}"


#task传入tasksummaryagent的response_dict['task_summary']
def dataanalysis_prompt_format(database_info: str, task) -> str:

    return f"""
# 一、任务背景
    你是一家数据库公司的专业数据分析师。你的工作是根据公司现有的数据库和上级下达的分析任务，从数据库中提取数据并计算目标数据（公司的数据库被固定命名为df，你需要写出python代码来从df中取数并计算目标数据）。为圆满完成该任务，你首先需要非常熟悉df的结构与内容，然后深刻理解任务目标与客户需求，最后牢记要保持自己的专业性。
# 二、相关信息
    - ***df的结构与内容概况（以下展示了df的所有列名及其类型，并从每列随机抽取了若干元素以供理解）***
        ```数据库信息
    {database_info}
        ```
    - ***任务目标***
        ```任务目标
{task}
        ```
# 三、你丰富的数据分析经验使你形成了一套专业的思维认知
    - 数据分析主要两大板块是取数和预测，取数是数据分析的基础，预测是数据分析的进阶。取数不仅仅是将数据从数据库中提取出来，其中还可能涉及到数据清洗和数据计算；预测则需要在取出数据的基础上，通过一些统计方法来预测数据未来的变化趋势。
    - 首先考虑用户的需求是否可以完成，客户有可能只需要取数，也有可能需要在取数的基础上进行预测。你需要对照df中的内容，确定df是否存在相关的数据。如果基础数据存在，则进一步规划取数和预测的步骤。
    - 在思考完取数和预测的步骤后，我们需要将这些步骤写成python代码，一步一步地完成取数与预测。
# 四、任务的具体执行要求（请在理解任务背景、相关信息与取数核心思想后，在执行任务时谨记并严格执行该要求）
    - 该任务需要一边思考取数的路径，一边考虑该任务是否真的能够完成。（因为有的任务已经超出了公司的数据范围，不可能完成取数分析）
    - 在思考的过程中，你需要推理提取数据的过程中我们需要什么样的数据，如果发现根本就没有这样的数据并且也没有办法用现有数据计算出相关数据，那么即表明该任务无法实现。
    - 做时序预测的时候无需提前进行各种检验，直接开始预测算法即可。
    - **你的编程环境是python，numpy库(as np)、pandas库(as pd)、statsmodels.api库(as sm)、statsmodels.tsa.api库(as tsa)已经导入，df也已经导入。**
    - **取数时最常用的库就是numpy库和pandas库，预测时则需要用到statsmodels.api库、statsmodels.tsa.api库。请记住，在做预测任务时，我们仅提供简单的预测方法，比如线性回归、时间序列分析等，而不会提供复杂的预测方法如机器学习（因为这非常耗费时间）。**
    - **不论是取数结果还是预测结果，最终都需要固定存在result_df中（预测任务中，需要将已有数据和预测数据合并成一张表，赋值给result_df，并以一列标注来区分），我们会把result_df再返还给客户。**
# 五、回复的格式（重中之重，在你的回答中，你一定需要在最后正式地给出判断与一份完整的代码，判断与代码需要严格遵守以下格式）
    ```你的回复固定格式
    [在此填写说明你的思考与分析]

    正式的判断与代码：
    1.该任务是否可实现：[此处填写Y或N]
    2.python代码:[若判断该任务不可实现，则此处不必填写python代码，而是填写不可实现的原因；若判断该任务可以实现，则在此处填写完整python代码。Tips：你的编程环境前面已提到，请不要导入其他的库，并直接对df进行操作，一步一步地完成取数与预测，将最终的结果固定赋值给result_df（如果是预测任务，则需要将已有数据和预测数据合成一张表格，并以一列标注来区分已有或预测，再赋值给result_df）。要求你在该部分写的代码经复制粘贴后可直接执行。]
    ```
    ***以上是你的回复格式，你仅能将你的回复按要求填充在[]中，其他内容严格保持不变，不要在前端与后端增添无关语句，回答时需要确保完整输出以上结构，不要遗漏，最终产出一个名为result_df的DataFrame。***
# 六、回复示例（以下是几个简化版的回复示例，仅供参考）
    ***示例一：数据筛选与计算任务***
    思考与分析：
    - **任务理解**: 筛选满足特定条件的...数据，然后按...维度分组，计算...指标（如环比、均值等）。
    - **数据可用性**: 检查`df`，确认包含所需的列（如...列和...列），且数据格式符合要求。
    - **分析路径**: 通过Pandas的布尔索引直接筛选`df`中符合...条件和...条件的行。然后使用`groupby()`按...列分组，然后对...列计算所需指标。
    - **结论**: 任务可行。

    正式的判断与代码：
    1.该任务是否可实现：Y
    2.python代码:
    ```python
    #... # 完整代码逻辑省略
    ```

    ***示例二：时间序列预测任务***
    思考与分析：
    - **任务理解**: 基于历史...数据（按时间排序），预测未来...时间段的趋势。
    - **数据可用性**: 确认`df`包含时间列（...列）和目标数值列（...列），构成有效时间序列。
    - **分析路径**:
        1. 预处理时间序列数据（设置索引、排序等）。
        2. 选择时间序列模型（如ARIMA）直接拟合历史数据。
        3. 使用模型预测未来N个时间点的值。
        4. 合并历史数据和预测数据，添加'状态'列区分。
    - **结论**: 任务可行。

    正式的判断与代码：
    1.该任务是否可实现：Y
    2.python代码:
    ```python
    # ... # 完整代码逻辑省略
    ```

    ***示例三：任务不可行示例***
    思考与分析：
    - **任务理解**: 需要计算/分析...指标。
    - **数据可用性**: 检查`df`的所有列，发现缺少计算该指标所必需的基础数据列（例如，需要...列，但`df`中没有）。
    - **分析路径**: 由于关键数据缺失，无法通过现有`df`计算出目标结果。
    - **结论**: 任务不可实现。

    正式的判断与代码：
    1.该任务是否可实现：N
    2.python代码:[不可实现的原因：数据库df中缺少必要的...数据（或类似说明），无法完成该分析任务。]

    """

class DataAnalysisAgent:
    def __init__(self, max_history: int = 10):

        self.max_history = max_history
        self.history = []
        
        '''# 初始化API
        dashscope.api_key = os.getenv('QWEN_API_KEY')
        self.api = dashscope.Generation'''
        self.client = OpenAI(
        base_url = base_url,
        api_key = api_key
        )

    def process_query(self, database_info, task) -> str:
        """处理输入"""
        try:
            # 生成完整prompt
            system_prompt = dataanalysis_prompt_format(database_info, task)
            print(system_prompt)
            messages = [
                {"role": "user", "content": system_prompt}
            ]
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.05,
                top_p=0.1,
                max_tokens=8192,
                presence_penalty=0.5,
                frequency_penalty=0.3,
                stream=True
            )
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
                    response += chunk.choices[0].delta.content
            response = response.split('</think>')[-1].strip()
            if '```你的回复固定格式' in response:
                response = response.split('```你的回复固定格式')[-1].strip()
                response = response.rstrip('```').strip()
            '''# 调用API
            response = self.api.call(
                model='qwen-max-2025-01-25',
                prompt=prompt
            )'''

            """# 定义完整思考过程
            reasoning_content = ""
            # 定义完整回复
            answer_content = ""
            # 判断是否结束思考过程并开始回复
            is_answering = False
            for chunk in response:
                # 如果思考过程与回复皆为空，则忽略
                if (chunk.output.choices[0].message.content == "" and 
                    chunk.output.choices[0].message.reasoning_content == ""):
                    pass
                else:
                    # 如果当前为思考过程
                    if (chunk.output.choices[0].message.reasoning_content != "" and 
                        chunk.output.choices[0].message.content == ""):

                        reasoning_content += chunk.output.choices[0].message.reasoning_content
                    # 如果当前为回复
                    elif chunk.output.choices[0].message.content != "":
                        if not is_answering:

                            is_answering = True

                        answer_content += chunk.output.choices[0].message.content"""

            response_text = response.split('正式的判断与代码')[-1].strip()
            try:
                pycode = re.search(r'python代码(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
            except:
                try:
                    pycode = re.search(r'原因(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
                except:
                    pycode = re.search(r'不可实现(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()

            response_dict = {
                'feasibility': re.search(r'该任务是否可实现(.*?)python代码', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').lstrip('[').rstrip('\n3.').strip().rstrip(']'),
                'python_code': pycode
            }
            print(response_dict)
            return response_dict
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"抱歉，处理您的请求时出现错误: {str(e)}"


#运行后就告诉前台 数已取好，请转告顾客查看数据





def bugfinder_prompt_format(database_info: str, task ,problem,problemds, wrongcode) -> str:
    if problem == 0:
        problemds = "result_df返回为空dataframe，这可能是由于所查询的条件错误或数据不存在导致的，需要你仔细甄别问题所在。请首先检查条件是否正确，包括筛选的逻辑是否出现偏差、筛选的字段是否存在偏误（重点关注是否是中英文名称未对齐，数据库内是英文名称而筛选条件是中文名称；其次关注是否是同义称呼未对齐，数据库对同一事物的称呼方式和筛选条件中的称呼方式不一致）。当确保筛选的逻辑无误、筛选的字段无偏误后，很有可能是数据库中没有该数据。"
    #当problem == 1时，直接采用传入的信息
    return f"""
# 一、任务背景：
    你是一个专业的程序员，具有专业的debug能力。你将和你的数据分析师同事一同完成从数据库中提取数据的任务，数据库的名称固定为df。你的数据分析师同事已经写好了提取数据的代码，但是在调试时发现了问题。你需要查看数据库的结构与内容、数据分析师原本的任务目标、问题的错误信息和问题代码，在深刻理解后找出问题的根源，并修改代码。
# 二、相关信息：
    - ***数据库df的结构与内容***
        ```数据库信息
    {database_info}
        ```
    - ***数据分析师原本的任务目标***
        ```任务目标
{task}
        ```
    - ***问题描述***
        ```报错信息
{problemds}
        ```
    - ***存在问题的代码***
        ```报错代码
{wrongcode}
        ```
# 三、任务的具体执行要求（请在理解以上信息后，在执行任务时谨记并严格执行该要求）：
    - 你需要首先分析问题所在，然后给出你的诊断结果，如果发现问题可以通过修改代码来解决，则给出修改后的完整版代码，如果发现问题的根源在于数据库中根本没有需要的数据，也需要依据规定的格式汇报。
    - **你的编程环境是python，numpy库(as np)、pandas库(as pd)、statsmodels.api库(as sm)、statsmodels.tsa.api库(as tsa)已经导入，df也已经导入。**
    - 取数时最常用的库就是numpy库和pandas库，预测时则需要用到statsmodels.api库、statsmodels.tsa.api库。请记住，在做预测任务时，我们仅提供简单的预测方法，比如线性回归、时间序列分析等，而不会提供复杂的预测方法如机器学习（因为这非常耗费时间）。
# 四、回复的格式（以下是你的回答需要严格遵守的格式）
    ```你的回复固定格式
    [在此填写说明你的思考和分析]
    1.诊断结果:[根据错误分析结果，在此处按照以下格式填写诊断结果：若该问题可通过修改代码来解决，则此处严格固定输出“可通过修改代码来解决”；若该问题是数据库中没有需要的数据，则此处严格固定输出“不能通过修改代码来解决”]
    2.更正后的python代码:[若诊断结果为“不能通过修改代码来解决”，则该部分不用继续填写，留空即可；若诊断结果中为“可通过修改代码来解决”，则在该部分填写完整的、经修改后的代码。Tips：你的编程环境前面已提到，请不要导入其他的库，并直接对df进行操作，一步一步地完成取数与预测，将最终的结果固定赋值给result_df（如果是预测任务，则需要将已有数据和预测数据合成一张表格，并以一列标注来区分已有或预测，再赋值给result_df），要求你在该部分写的代码经复制粘贴后可直接执行。]
    ```
    ***以上是你的回复格式，你仅能将你的回复按要求填充在[]中，其他内容严格保持不变，不要在前端与后端增添无关语句，回答时需要确保完整输出以上结构，不要遗漏，且以上2点的逻辑不能相悖。***
    """

class BugFinderAgent:
    def __init__(self, max_history: int = 10):

        self.max_history = max_history
        self.history = []
        
        '''# 初始化API
        dashscope.api_key = os.getenv('QWEN_API_KEY')
        self.api = dashscope.Generation'''
        self.client = OpenAI(
        base_url =  base_url,
        api_key = api_key
        )

    def process_query(self, database_info, task,problem,problemds, wrongcode) -> str:
        """处理输入"""
        try:
            # 生成完整prompt
            system_prompt = bugfinder_prompt_format(database_info, task,problem,problemds, wrongcode)
            print(system_prompt)
            messages = [
                {"role": "user", "content": system_prompt}
            ]
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.05,
                top_p=0.3,
                max_tokens=8192,
                presence_penalty=0.5,
                frequency_penalty=0.3,
                stream=True
            )
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
                    response += chunk.choices[0].delta.content
            response = response.split('</think>')[-1].strip()
            if '```你的回复固定格式' in response:
                response = response.split('```你的回复固定格式')[-1].strip()
                response = response.rstrip('```').strip()
            '''# 调用API
            response = self.api.call(
                model='qwen-max-2025-01-25',
                prompt=prompt
            )'''
            """# 定义完整思考过程
            reasoning_content = ""
            # 定义完整回复
            answer_content = ""
            # 判断是否结束思考过程并开始回复
            is_answering = False
            for chunk in response:
                # 如果思考过程与回复皆为空，则忽略
                if (chunk.output.choices[0].message.content == "" and 
                    chunk.output.choices[0].message.reasoning_content == ""):
                    pass
                else:
                    # 如果当前为思考过程
                    if (chunk.output.choices[0].message.reasoning_content != "" and 
                        chunk.output.choices[0].message.content == ""):
                        reasoning_content += chunk.output.choices[0].message.reasoning_content
                    # 如果当前为回复
                    elif chunk.output.choices[0].message.content != "":
                        if not is_answering:
                            is_answering = True
                        answer_content += chunk.output.choices[0].message.content"""
            response_text = response
            try:
                pycode = re.search(r'更正后的python代码(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
            except:
                try:
                    pycode = re.search(r'原因(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
                except:
                    pycode = re.search(r'不可实现(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()

            response_dict = {
                'diagnose': re.search(r'诊断结果(.*?)更正后的python代码', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').lstrip('[').rstrip('\n3.').strip().rstrip(']'),
                'python_code': pycode
            }
            return response_dict
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"抱歉，处理您的请求时出现错误: {str(e)}"



























def Adjustment_prompt_format(database_info: str, previous_code, adjustment_request) -> str:

    return f"""
# 一、任务背景
    之前提供给用户的代码无法很好地满足用户的需求，用户希望你能够根据用户的需求进一步调整代码。现在，你需要在源数据表df、原代码的基础上，根据用户调整表格的新要求，修改并输出完整的、符合用户需求的新代码。
# 二、相关信息
    - ***源数据表df的结构与内容概况（以下展示了df的所有列名及其类型，并从每列随机抽取了若干元素以供理解）***
        ```数据库信息
    {database_info}
        ```
    - ***不满足用户需求的原代码***
        ```待修改代码
{previous_code}
        ```
# 三、用户想要如何调整表格
    ```用户请求
    用户：{adjustment_request}
    ```
# 四、任务的具体执行要求（请在理解任务背景、相关信息后，在执行任务时谨记并严格执行该要求）
    - 你需要先推理判断，为了完成用户的调整需求我们需要怎样去修改，如果发现数据库中的数据没有办法满足用户的需求，则不必写代码；如果用户的修改需求能够做到，则将修改后的代码版本完整重新输出。
    - 如果需要做时序预测，我们仅提供简单的预测方法，比如线性回归、时间序列分析等，而不会提供复杂的预测方法如机器学习（因为这非常耗费时间），同时也无需提前进行各种检验，直接开始预测算法即可。
    - **你的编程环境是python，numpy库(as np)、pandas库(as pd)、statsmodels.api库(as sm)、statsmodels.tsa.api库(as tsa)已经导入，df也已经导入。**
    - **不论是取数结果还是预测结果，最终都需要固定存在result_df中（预测任务中，需要将已有数据和预测数据合并成一张表，赋值给result_df，并以一列标注来区分），我们会把result_df再返还给客户。**
# 五、回复的格式（重中之重，在你的回答中，你一定需要在最后正式地给出判断与一份完整的代码，判断与代码需要严格遵守以下格式）
    ```你的回复固定格式
    [在此填写说明你的思考与分析]

    正式的判断与代码：
    1.该调整任务是否可实现：[在此填写Y或N]
    2.修改后的python代码:[若判断该任务不可实现，则此处不用填写python代码，留空即可；若判断该任务可以实现，则在该部分输填写基于原代码修改完后的完整代码。Tips：你的编程环境前面已提到，请不要导入其他的库，并直接对df进行操作。你必须将最终的结果固定赋值给result_df，要求你在该部分写的代码经复制粘贴后可直接执行。]
    ```
    ***以上是你的回复格式，你仅能将你的回复按要求填充在[]中，其他内容严格保持不变，不要在前端与后端增添无关语句，回答时需要确保完整输出以上结构，不要遗漏，最终产出一个名为result_df的DataFrame。***
# 六、回复示例    
    ***示例1***
分析：用户希望基于源数据df新增筛选和计算操作。
1.  数据检查：df 包含执行这些操作所需的列（如 '...'、'...'、'...'）。
2.  操作检查：df 包含的数据可以用于计算...，具体算法为...。
3.  对比原代码：原代码 '...' 与新需求 '...' 不同，需要修改筛选逻辑和/或分组聚合逻辑。
结论：该调整任务所需的数据和操作均具备，可以实现。

正式的判断与代码：
1.该调整任务是否可实现：Y
2.修改后的python代码:
```python
# ... # 完整代码逻辑省略
# 最终结果赋值给 result_df （确保这一步存在）
```

    ***示例2***
分析：用户希望基于df中的历史数据（例如 '...' 列随 '...' 列的变化）进行简单的时序预测，预测未来 N 个周期。
1.  数据检查：df 包含时间序列数据（时间列 '...' 和数值列 '...'）。
2.  操作检查：任务要求允许使用简单预测方法（如线性回归、时间序列分析 - ARIMA等），且statsmodels库已导入。可以执行简单预测。
3.  对比原代码：原代码 '...' 未包含预测逻辑，需要新增模型训练和预测步骤，并按要求合并历史与预测数据。
结论：该调整任务可以使用允许的简单预测方法实现。

正式的判断与代码：
1.该调整任务是否可实现：Y
2.修改后的python代码:
```python
# ... # 完整代码逻辑省略
# 最终结果赋值给 result_df （确保这一步存在）
```

    ***示例3***
分析：用户希望执行的操作（例如根据 '...' 进行筛选或计算）依赖于df中的 '...' 信息。
1.  数据检查：检查源数据表df的结构信息，发现其中并不包含用户请求所必需的 '...' 列或相关信息。
2.  操作检查：由于缺少关键数据 '...'，无法完成用户指定的 '...' 操作。
结论：缺少必要的数据，该调整任务无法实现。

正式的判断与代码：
1.该调整任务是否可实现：N
2.修改后的python代码:[]

    """

class AdjustmentAgent:
    def __init__(self, max_history: int = 10):

        self.max_history = max_history
        self.history = []
        
        '''# 初始化API
        dashscope.api_key = os.getenv('QWEN_API_KEY')
        self.api = dashscope.Generation'''
        self.client = OpenAI(
        base_url = base_url,
        api_key = api_key
        )

    def process_query(self, database_info,previous_code, adjustment_request) -> str:
        """处理输入"""
        try:
            # 生成完整prompt
            system_prompt = Adjustment_prompt_format(database_info,previous_code, adjustment_request )
            print(system_prompt)
            messages = [
                {"role": "user", "content": system_prompt}
            ]
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.05,
                top_p=0.3,
                max_tokens=8192,
                presence_penalty=0.5,
                frequency_penalty=0.3,
                stream=True
            )
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
                    response += chunk.choices[0].delta.content
            response = response.split('</think>')[-1].strip()
            if '```你的回复固定格式' in response:
                response = response.split('```你的回复固定格式')[-1].strip()
                response = response.rstrip('```').strip()
            '''# 调用API
            response = self.api.call(
                model='qwen-max-2025-01-25',
                prompt=prompt
            )'''

            """# 定义完整思考过程
            reasoning_content = ""
            # 定义完整回复
            answer_content = ""
            # 判断是否结束思考过程并开始回复
            is_answering = False
            for chunk in response:
                # 如果思考过程与回复皆为空，则忽略
                if (chunk.output.choices[0].message.content == "" and 
                    chunk.output.choices[0].message.reasoning_content == ""):
                    pass
                else:
                    # 如果当前为思考过程
                    if (chunk.output.choices[0].message.reasoning_content != "" and 
                        chunk.output.choices[0].message.content == ""):

                        reasoning_content += chunk.output.choices[0].message.reasoning_content
                    # 如果当前为回复
                    elif chunk.output.choices[0].message.content != "":
                        if not is_answering:

                            is_answering = True

                        answer_content += chunk.output.choices[0].message.content"""

            response_text = response.split('正式的判断与代码')[-1].strip()
            try:
                pycode = re.search(r'修改后的python代码(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
            except:
                try:
                    pycode = re.search(r'原因(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
                except:
                    pycode = re.search(r'不可实现(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()


            response_dict = {
                'feasibility': re.search(r'该调整任务是否可实现(.*?)修改后的python代码', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').lstrip('[').rstrip('\n3.').strip().rstrip(']'),
                'python_code': pycode
            }
            return response_dict
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"抱歉，处理您的请求时出现错误: {str(e)}"














def Draw_prompt_format(result_database_info: str, drawing_request) -> str:

    return f"""
# 一、任务背景：
    用户是一个完全不懂python语言的小白，他想通过python的matplotlib库来绘制图表，但他不知道绘图代码该如何写。现在，他已经通过pandas导入了他的df，你需要帮助他在df的基础上，使用matplotlib库来绘制他所需要的图，并且将图片保存到BytesIO对象中以便于传输。你需要给出完整的、经复制粘贴后可直接执行的代码。
# 二、源数据表df的结构与内容概况（以下展示了df的所有列名及其类型，并从每列随机抽取了若干元素以供理解）：
    ```数据库信息
    {result_database_info}
    ```
# 三、用户想要如何绘制图表：
    你需要重点关注以下用户的绘图需求，由于该部分的重要性，以下将重复强调两遍：
    ```用户请求
    用户：{drawing_request}
    ```
    ```用户请求（第二遍）
    用户：{drawing_request}
    ```
# 四、任务的具体执行要求（请在理解任务背景、df结构与内容、用户意图后，在执行任务时谨记并严格执行该要求）：
    - 你非常乐意帮助用户来绘制图表，并且你是一个非常专业的程序员，你的代码经用户复制粘贴后可直接执行而不报错。
    - 若用户的绘制需求并不复杂，则你给出的绘图代码也遵循简单原则；若用户详细要求了绘图的各种细节，则你需要重点关注并尽力满足这些绘图细节要求。
    - **你需要重视中文和负号的显示问题，代码中一定包含这两段代码**：(1).plt.rcParams['font.sans-serif'] = ['SimHei']   (2).plt.rcParams['axes.unicode_minus'] = False 
    - 你需要注意图中文字密度的问题，尽量避免图中文字重叠，若文字太多，你可以减少标注和缩小字体。
    - **你的编程环境是python，numpy库(as np)、pandas库(as pd)、matplotlib(as plt)、io.BytesID已经导入，df也已经导入。**
    - **你必须将绘成的图表保存到BytesIO对象中，并将该对象固定赋值给名为plot_data的变量，以便用户获取你作的图。**
# 五、回复的格式（重中之重，在你的回答中，你一定需要在最后正式地给出一份完整的代码，你的回答需要严格遵守以下格式）：
    ```你的回复固定格式
    [在此填写说明你的思考与分析]

    python代码:[在此填写python代码，你的编程环境前面已提到，请不要导入其他的库，并直接对df进行操作，代码最后必须包含将图表保存到BytesIO对象并赋值给plot_data变量的步骤。要求你在该部分写的代码经复制粘贴后可直接执行。]
    ```
    ***以上是你的回复格式，你仅能将你的回复按要求填充在[]中，其他内容严格保持不变，不要在前端与后端增添无关语句，回答时需要确保完整输出以上结构，不要遗漏，最终产出一个名为plot_data的BytesID。***
# 六、回复示例（以下是一条回复示例）：
    用户需要我根据df中的数据来绘制一个堆积图，要求我使用matplotlib进行绘制并保存到plot_data变量中，我需要注意字符显示问题与字符密度问题。我将使用df中的…作为x轴、…作为y轴……

    python代码：
    ```python
    plt.figure(figsize=(10, 6))
    plt.plot(df['x'], df['y'])
    plt.title('示例图表')
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # ...具体的绘图代码...
    # 保存图表到 BytesIO 对象
    plot_data = BytesIO()
    plt.savefig(plot_data, format='png', bbox_inches='tight')
    plt.close()
    plot_data.seek(0)
    ```
    """


class DrawAgent:
    def __init__(self, max_history: int = 10):

        self.max_history = max_history
        self.history = []
        
        '''# 初始化API
        dashscope.api_key = os.getenv('QWEN_API_KEY')
        self.api = dashscope.Generation'''
        self.client = OpenAI(
        base_url = base_url,
        api_key = api_key
        )

    def process_query(self, result_database_info,drawing_request) -> str:
        """处理输入"""
        try:
            # 生成完整prompt
            system_prompt = Draw_prompt_format(result_database_info,drawing_request )
            print(system_prompt)
            messages = [
                {"role": "user", "content": system_prompt}
            ]
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.05,
                top_p=0.3,
                max_tokens=8192,
                presence_penalty=0.5,
                frequency_penalty=0.3,
                stream=True
            )
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
                    response += chunk.choices[0].delta.content
            response = response.split('</think>')[-1].strip()
            if '```你的回复固定格式' in response:
                response = response.split('```你的回复固定格式')[-1].strip()
                response = response.rstrip('```').strip()
            '''# 调用API
            response = self.api.call(
                model='qwen-max-2025-01-25',
                prompt=prompt
            )'''

            """# 定义完整思考过程
            reasoning_content = ""
            # 定义完整回复
            answer_content = ""
            # 判断是否结束思考过程并开始回复
            is_answering = False
            for chunk in response:
                # 如果思考过程与回复皆为空，则忽略
                if (chunk.output.choices[0].message.content == "" and 
                    chunk.output.choices[0].message.reasoning_content == ""):
                    pass
                else:
                    # 如果当前为思考过程
                    if (chunk.output.choices[0].message.reasoning_content != "" and 
                        chunk.output.choices[0].message.content == ""):

                        reasoning_content += chunk.output.choices[0].message.reasoning_content
                    # 如果当前为回复
                    elif chunk.output.choices[0].message.content != "":
                        if not is_answering:

                            is_answering = True

                        answer_content += chunk.output.choices[0].message.content"""

            response_text = response.strip()
            try:
                pycode = re.search(r' python代码(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
            except:
                try:
                    pycode = re.search(r'python代码(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
                except:
                    pycode = re.search(r'python code(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()


            response_dict = {
                'python_code': pycode
            }
            return response_dict
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"抱歉，处理您的请求时出现错误: {str(e)}"













def Draw_Adjustment_prompt_format(result_database_info: str, drawing_request, last_code) -> str:

    return f"""
# 一、任务背景：
    你作为一个AI代码助手，已经按照用户的需求帮用户写了绘制图表的代码，但用户的需求还没有得到全部满足，现在你需要在已有的代码的基础上作出修改，来满足用户进一步的需求。具体而言，用户的原始数据被保存在变量df中，你需要根据用户进一步的需求，继续使用matplotlib库来修改与完善现有绘图代码，并且将图片保存到BytesIO对象中以便于传输。你需要给出完整的、经复制粘贴后可直接执行的代码，而非片段代码或者修改建议。
# 二、源数据表df的结构与内容概况（以下展示了df的所有列名及其类型，并从每列随机抽取了若干元素以供理解）：
    ```数据库信息
    {result_database_info}
    ```
# 三、用户想要如何进一步修改绘图代码：
    你需要重点关注以下用户的修改需求，由于该部分的重要性，以下将重复强调两遍：
    ```用户请求
    用户：{drawing_request}
    ```
    ```用户请求（第二遍）
    用户：{drawing_request}
    ```
# 四、用户的原始绘图代码：
    ```用户原始绘图代码
    {last_code}
    ```
# 五、任务的具体执行要求（请在理解任务背景、df结构与内容、用户意图后，在执行任务时谨记并严格执行该要求）：
    - 你非常乐意帮助用户来绘制图表，并且你是一个非常专业的程序员，你的代码经用户复制粘贴后可直接执行而不报错。
    - **你需要给出完整的、经复制粘贴后可直接执行的代码，而不能仅仅给出代码修改片段或者修改意见**。
    - **你需要重视中文和负号的显示问题，代码中一定包含这两段代码**：(1).plt.rcParams['font.sans-serif'] = ['SimHei']   (2).plt.rcParams['axes.unicode_minus'] = False 
    - 你需要注意图中文字密度的问题，尽量避免图中文字重叠，若文字太多，你可以减少标注和缩小字体。
    - **你的编程环境是python，numpy库(as np)、pandas库(as pd)、matplotlib(as plt)、io.BytesID已经导入，df也已经导入。**
    - **你必须同样地将绘成的图表保存到BytesIO对象中，并将该对象固定赋值给名为plot_data的变量，以便用户获取你作的图。**
# 六、回复的格式（重中之重，在你的回答中，你一定需要在最后正式地给出一份完整的代码，你的回答需要严格遵守以下格式）：
    ```你的回复固定格式
    [在此填写说明你的思考与分析]

    python代码:[在此填写python代码，你的编程环境前面已提到，请不要导入其他的库，在用户原始绘图代码的修改出一版新的代码，兼顾用户原始的需求以及新的需求。代码最后必须包含将图表保存到BytesIO对象并赋值给plot_data变量的步骤。要求你在该部分写的代码经复制粘贴后可直接执行。]
    ```
    ***以上是你的回复格式，你仅能将你的回复按要求填充在[]中，其他内容严格保持不变，不要在前端与后端增添无关语句，回答时需要确保完整输出以上结构，不要遗漏，最终产出一个名为plot_data的BytesID。***
# 七、回复示例（以下是一条回复示例）：
    用户需要在已有散点图中再添加一条平滑的拟合曲线，我注意到现有代码已经绘制了x与y的散点图，我需要在现在这张散点图的绘制代码的基础上，先拟合出一条x与y的平滑曲线，然后将这条曲线添加到现有的散点图上。我将继续使用matplotlib进行绘制，我会给出完整的代码，并产出一个名为plot_data的BytesID。

    python代码：
    ```python
    plt.figure(figsize=(10, 6))
    plt.plot(df['x'], df['y'])
    plt.title('示例图表')
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    # ...原始的绘图代码...
    #...新添加一条简单的拟合曲线的代码...
    # 保存图表到 BytesIO 对象
    plot_data = BytesIO()
    plt.savefig(plot_data, format='png', bbox_inches='tight')
    plt.close()
    plot_data.seek(0)
    ```
    """


class DrawAdjustmentAgent:
    def __init__(self, max_history: int = 10):

        self.max_history = max_history
        self.history = []
        
        '''# 初始化API
        dashscope.api_key = os.getenv('QWEN_API_KEY')
        self.api = dashscope.Generation'''
        self.client = OpenAI(
        base_url = base_url,
        api_key = api_key
        )

    def process_query(self, result_database_info,drawing_request, last_code) -> str:
        """处理输入"""
        try:
            # 生成完整prompt
            system_prompt = Draw_Adjustment_prompt_format(result_database_info,drawing_request ,last_code)
            print(system_prompt)
            messages = [
                {"role": "user", "content": system_prompt}
            ]
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.05,
                top_p=0.3,
                max_tokens=8192,
                presence_penalty=0.5,
                frequency_penalty=0.3,
                stream=True
            )
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
                    response += chunk.choices[0].delta.content
            response = response.split('</think>')[-1].strip()
            if '```你的回复固定格式' in response:
                response = response.split('```你的回复固定格式')[-1].strip()
                response = response.rstrip('```').strip()

            response_text = response.strip()
            try:
                pycode = re.search(r' python代码(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
            except:
                try:
                    pycode = re.search(r'python代码(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()
                except:
                    pycode = re.search(r'python code(.*)', response_text, re.DOTALL).group(1).strip().lstrip(':').lstrip('：').strip()


            response_dict = {
                'python_code': pycode
            }
            print(response_dict)
            return response_dict
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"抱歉，处理您的请求时出现错误: {str(e)}"

