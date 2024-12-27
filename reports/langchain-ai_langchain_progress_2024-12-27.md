# Daily Progress Report - langchain-ai/langchain
Generated at: 2024-12-27 11:49:28
Period: 2024-12-26 03:49:17 to 2024-12-27 03:49:28

## Statistics
- Issues: 10 updates
- Pull Requests: 9 updates

## Issues
### #28934 - [ChatOllama does not parse yfinance output correctly](https://github.com/langchain-ai/langchain/issues/28934)
**Status:** 🟢 Open  
**Author:** dlin95123  
**Created:** 2024-12-27 02:33:24  
**Updated:** 2024-12-27 02:35:47  
**Labels:** 🤖:bug, Ɑ:  models  

<details><summary>Description</summary>

### Checked other resources

- [X] I added a very descriptive title to this issue.
- [X] I searched the LangChain documentation with the integrated search.
- [X] I used the GitHub search to find a similar question and didn't find it.
- [X] I am sure that this is a bug in LangChain rather than my code.
- [X] The bug is not resolved by updating to the latest stable version of LangChain (or the specific integration package).

### Example Code


from dotenv import load_dotenv
import os

load_dotenv()

from langchain_ollama import ChatOllama 
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough 
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.tools import tool
import yfinance as yf

llm = ChatOllama(model='llama3.1', temperature=0)
#llm = ChatGroq(model='llama-3.1-8b-instant', temperature =0)
#llm = ChatOpenAI(model='gpt-4o-mini', temperature = 0)

from langchain_core.tools import tool, StructuredTool
from datetime import date

@tool
def company_information(ticker: str) -> dict:
    """Use this tool to retrieve company information like address, industry, sector, company officers, business summary, website,
       marketCap, current price, ebitda, total debt, total revenue, debt-to-equity, etc."""
    
    ticker_obj = yf.Ticker(ticker)
    ticker_info = ticker_obj.get_info()

    return ticker_info

@tool
def last_dividend_and_earnings_date(ticker: str) -> dict:
    """
    Use this tool to retrieve company's last dividend date and earnings release dates.
    It does not provide information about historical dividend yields.
    """
    ticker_obj = yf.Ticker(ticker)
    
    return ticker_obj.get_calendar()

@tool
def summary_of_mutual_fund_holders(ticker: str) -> dict:
    """
    Use this tool to retrieve company's top mutual fund holders. 
    It also returns their percentage of share, stock count and value of holdings.
    """
    ticker_obj = yf.Ticker(ticker)
    mf_holders = ticker_obj.get_mutualfund_holders()
    
    return mf_holders.to_dict(orient="records")

@tool
def summary_of_institutional_holders(ticker: str) -> dict:
    """
    Use this tool to retrieve company's top institutional holders. 
    It also returns their percentage of share, stock count and value of holdings.
    """
    ticker_obj = yf.Ticker(ticker)   
    inst_holders = ticker_obj.get_institutional_holders()
    
    return inst_holders.to_dict(orient="records")

@tool
def stock_grade_updrages_downgrades(ticker: str) -> dict:
    """
    Use this to retrieve grade ratings upgrades and downgrades details of particular stock.
    It'll provide name of firms along with 'To Grade' and 'From Grade' details. Grade date is also provided.
    """
    ticker_obj = yf.Ticker(ticker)
    
    curr_year = date.today().year
    
    upgrades_downgrades = ticker_obj.get_upgrades_downgrades()
    upgrades_downgrades = upgrades_downgrades.loc[upgrades_downgrades.index > f"{curr_year}-01-01"]
    upgrades_downgrades = upgrades_downgrades[upgrades_downgrades["Action"].isin(["up", "down"])]
    
    return upgrades_downgrades.to_dict(orient="records")

@tool
def stock_splits_history(ticker: str) -> dict:
    """
    Use this tool to retrieve company's historical stock splits data.
    """
    ticker_obj = yf.Ticker(ticker)
    hist_splits = ticker_obj.get_splits()
    
    return hist_splits.to_dict()

@tool
def stock_news(ticker: str) -> dict:
    """
    Use this to retrieve latest news articles discussing particular stock ticker.
    """
    ticker_obj = yf.Ticker(ticker)
    
    return ticker_obj.get_news()


from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent

#from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

tools = [
         company_information,
         last_dividend_and_earnings_date,
         stock_splits_history,
         summary_of_mutual_fund_holders,
         summary_of_institutional_holders, 
         stock_grade_updrages_downgrades,
         stock_news
]
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Try to answer user query using available tools. Parse the input carefully.",
        ),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

from langchain_core.messages import HumanMessage

resp = agent_executor.invoke({"messages": [HumanMessage(content="What is address of Nike?")]})


### Error Message and Stack Trace (if applicable)

_No response_

### Description

I am testing local LLMs with ChatOllama and using llama3.1 for answering output from yfinance. I found that it cannot answer simple question like "What is Nike's address?". It can answer longer questions okay, just not short question. 

It works pretty well with ChatOpenAI() and ChatGroq() with the same model. You can reproduce the issue with the attached code. 

### System Info

System Information
------------------
> OS:  Windows
> OS Version:  10.0.22631
> Python Version:  3.12.8 (tags/v3.12.8:2dc476b, Dec  3 2024, 19:30:04) [MSC v.1942 64 bit (AMD64)]

Package Information
-------------------
> langchain_core: 0.3.28
> langchain: 0.3.12
> langchain_community: 0.3.12
> langsmith: 0.2.3
> langchain_groq: 0.2.2
> langchain_huggingface: 0.1.0
> langchain_ollama: 0.2.1
> langchain_openai: 0.2.12
> langchain_text_splitters: 0.3.3
> langgraph_sdk: 0.1.45

Optional packages not installed
-------------------------------
> langserve

Other Dependencies
------------------
> aiohttp: 3.11.10
> async-timeout: Installed. No version info available.
> dataclasses-json: 0.6.7
> groq: 0.13.1
> httpx: 0.27.2
> httpx-sse: 0.4.0
> huggingface-hub: 0.25.1
> jsonpatch: 1.33
> langsmith-pyo3: Installed. No version info available.
> numpy: 1.26.4
> ollama: 0.4.4
> openai: 1.58.1
> orjson: 3.10.12
> packaging: 24.2
> pydantic: 2.9.2
> pydantic-settings: 2.7.0
> PyYAML: 6.0.2
> requests: 2.32.3
> requests-toolbelt: 1.0.0
> sentence-transformers: 3.3.1
> SQLAlchemy: 2.0.36
> tenacity: 9.0.0
> tiktoken: 0.8.0
> tokenizers: 0.21.0
> transformers: 4.47.0
> typing-extensions: 4.12.2
</details>

### #28928 - [community: add modelscope endpoint](https://github.com/langchain-ai/langchain/pull/28928)
**Status:** 🔴 Closed  
**Author:** Yunnglin  
**Created:** 2024-12-26 08:08:19  
**Updated:** 2024-12-27 02:17:47  
**Labels:** size:XL, community  

<details><summary>Description</summary>

## Description

Add ModelScope inference API endpoint for both LLMs and ChatModels.

ModelScope is a leading platform to bridge model checkpoints and model applications. It offers the infrastructure for sharing open models and facilitating model-centric development (https://github.com/modelscope).


</details>

### #28923 - [Tongyi llm call error with model "qwen-long"](https://github.com/langchain-ai/langchain/issues/28923)
**Status:** 🟢 Open  
**Author:** niuguy  
**Created:** 2024-12-25 22:48:02  
**Updated:** 2024-12-27 00:14:25  

<details><summary>Description</summary>

### Checked other resources

- [X] I added a very descriptive title to this issue.
- [X] I searched the LangChain documentation with the integrated search.
- [X] I used the GitHub search to find a similar question and didn't find it.
- [X] I am sure that this is a bug in LangChain rather than my code.
- [X] The bug is not resolved by updating to the latest stable version of LangChain (or the specific integration package).

### Example Code

```python
from langchain_community.llms.tongyi import Tongyi
import os

tongyi = Tongyi(model="qwen-turbo", api_key=api_key)

response = tongyi.invoke("Who are you?")

print(response)

```

### Error Message and Stack Trace (if applicable)

```python
Traceback (most recent call last):
  File "/Users/feng/Work/my/tests/qwen/api_test.py", line 33, in <module>
    response = tongyi.invoke("Who are you?")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/feng/Work/my/tests/qwen/.venv/lib/python3.12/site-packages/langchain_core/language_models/llms.py", line 390, in invoke
    self.generate_prompt(
  File "/Users/feng/Work/my/tests/qwen/.venv/lib/python3.12/site-packages/langchain_core/language_models/llms.py", line 755, in generate_prompt
    return self.generate(prompt_strings, stop=stop, callbacks=callbacks, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/feng/Work/my/tests/qwen/.venv/lib/python3.12/site-packages/langchain_core/language_models/llms.py", line 950, in generate
    output = self._generate_helper(
             ^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/feng/Work/my/tests/qwen/.venv/lib/python3.12/site-packages/langchain_core/language_models/llms.py", line 792, in _generate_helper
    raise e
  File "/Users/feng/Work/my/tests/qwen/.venv/lib/python3.12/site-packages/langchain_core/language_models/llms.py", line 779, in _generate_helper
    self._generate(
  File "/Users/feng/Work/my/tests/qwen/.venv/lib/python3.12/site-packages/langchain_community/llms/tongyi.py", line 327, in _generate
    [Generation(**self._generation_from_qwen_resp(completion))]
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/feng/Work/my/tests/qwen/.venv/lib/python3.12/site-packages/langchain_core/load/serializable.py", line 125, in __init__
    super().__init__(*args, **kwargs)
  File "/Users/feng/Work/my/tests/qwen/.venv/lib/python3.12/site-packages/pydantic/main.py", line 214, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 1 validation error for Generation
text
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.10/v/string_type

```

### Description

I tried other models listed [here](https://help.aliyun.com/zh/model-studio/getting-started/models?spm=a2c4g.11186623.help-menu-2400256.d_0_2.41f9253aV5dLgB)  [qwen-max, qwen-turbo, qwen-plus] which are all working fine


I debugged and stepped into the source code and found that [this line](https://github.com/langchain-ai/langchain/blob/5991b45a88fe60fe511c7a64a0a5f1dbb2410b08/libs/community/langchain_community/llms/tongyi.py#L454)  should be the root cause as for "qwen-long" the api returns "choices" instead of "text" which results in a Nonetype

you can debug and replicate it like
```python
from langchain_community.llms.tongyi import Tongyi
import os

original_generate = Tongyi._generate

def debug_generate(self, prompts, stop=None, run_manager=None, **kwargs):
    breakpoint()  
    return original_generate(self, prompts, stop, run_manager, **kwargs)

# Patch the method
Tongyi._generate = debug_generate
api_key = os.getenv("DASHSCOPE_API_KEY")

tongyi = Tongyi(model="qwen-turbo", api_key=api_key)

response = tongyi.invoke("Who are you?")

print(response)
```
This issue could potentially be resolved by checking both resp["output"]["text"] and resp["output"]["choices"] for the response. However, it’s unclear if this inconsistency stems from the Tongyi server. The module’s maintainer might be able to provide clarification.

### System Info

```
System Information
------------------
> OS:  Darwin
> OS Version:  Darwin Kernel Version 24.1.0: Thu Oct 10 21:03:15 PDT 2024; root:xnu-11215.41.3~2/RELEASE_ARM64_T6000
> Python Version:  3.12.5 (main, Aug 14 2024, 04:32:18) [Clang 18.1.8 ]

Package Information
-------------------
> langchain_core: 0.3.28
> langchain: 0.3.13
> langchain_community: 0.3.13
> langsmith: 0.2.6
> langchain_text_splitters: 0.3.4

Optional packages not installed
-------------------------------
> langserve

Other Dependencies
------------------
> aiohttp: 3.11.11
> async-timeout: Installed. No version info available.
> dataclasses-json: 0.6.7
> httpx: 0.28.1
> httpx-sse: 0.4.0
> jsonpatch: 1.33
> langsmith-pyo3: Installed. No version info available.
> numpy: 2.2.1
> orjson: 3.10.12
> packaging: 24.2
> pydantic: 2.10.4
> pydantic-settings: 2.7.0
> PyYAML: 6.0.2
> requests: 2.32.3
> requests-toolbelt: 1.0.0
> SQLAlchemy: 2.0.36
> tenacity: 9.0.0
> typing-extensions: 4.12.2
> zstandard: Installed. No version info available.
```
</details>

### #28924 - [partners: fix default value for stop_sequences in ChatGroq](https://github.com/langchain-ai/langchain/pull/28924)
**Status:** 🔴 Closed  
**Author:** dabzr  
**Created:** 2024-12-26 03:20:58  
**Updated:** 2024-12-26 21:43:34  
**Labels:** lgtm, 🤖:bug, size:XS  

<details><summary>Description</summary>

- **Description:**  
      This PR addresses an issue with the `stop_sequences` field in the `ChatGroq` class. Currently, the field is defined as:
```python
stop: Optional[Union[List[str], str]] = Field(None, alias="stop_sequences")
```  
This causes the language server (LSP) to raise an error indicating that the `stop_sequences` parameter must be implemented. The issue occurs because `Field(None, alias="stop_sequences")` is different compared to `Field(default=None, alias="stop_sequences")`.  

![image](https://github.com/user-attachments/assets/bfc34cb1-c664-4c31-b856-8f18419c7350)
To resolve the issue, the field is updated to:  
```python
stop: Optional[Union[List[str], str]] = Field(default=None, alias="stop_sequences")
```  
While this issue does not affect runtime behavior, it ensures compatibility with LSPs and improves the development experience.  
- **Issue:** N/A  
- **Dependencies:** None  


</details>

### #28918 - [community: Fix error handling bug in ChatDeepInfra](https://github.com/langchain-ai/langchain/pull/28918)
**Status:** 🔴 Closed  
**Author:** andywer  
**Created:** 2024-12-25 15:41:18  
**Updated:** 2024-12-26 19:45:13  
**Labels:** lgtm, 🤖:bug, size:XS, community  

<details><summary>Description</summary>

In the async ClientResponse, `response.text` is not a string property, but an asynchronous function returning a string.
</details>

### #28899 - [Update chroma.ipynb, Add langchain openai to the pip install in the chroma docs](https://github.com/langchain-ai/langchain/pull/28899)
**Status:** 🔴 Closed  
**Author:** Latticeworks1  
**Created:** 2024-12-24 04:47:37  
**Updated:** 2024-12-26 19:42:45  
**Labels:** 🤖:docs, size:XS  

<details><summary>Description</summary>

Description: added langchain openai to the pip
Issue: Example notebook will not run without this added
Dependencies: langchain openai

</details>

### #28909 - [Docs: Updaing 'JSON Schema' code block output](https://github.com/langchain-ai/langchain/pull/28909)
**Status:** 🔴 Closed  
**Author:** ahmadelmalah  
**Created:** 2024-12-24 23:46:03  
**Updated:** 2024-12-26 19:37:12  
**Labels:** lgtm, 🤖:docs, size:XS  

<details><summary>Description</summary>

Out seems outdate, I ran the example several times and this is the updated output, one key-value pair was missing!
![image](https://github.com/user-attachments/assets/95231ce7-714e-43ac-b07e-57debded4735)

</details>

### #28916 - [docs: Update VectorStoreTabs.js](https://github.com/langchain-ai/langchain/pull/28916)
**Status:** 🔴 Closed  
**Author:** bongsang  
**Created:** 2024-12-25 11:04:39  
**Updated:** 2024-12-26 19:31:59  
**Labels:** lgtm, 🤖:docs, size:XS  

<details><summary>Description</summary>

- Title: Fix typo to correct "embedding" to "embeddings" in PGVector initialization example

- Problem: There is a typo in the example code for initializing the PGVector class. The current parameter "embedding" is incorrect as the class expects "embeddings".

- Correction: The corrected code snippet is:

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="my_docs",
    connection="postgresql+psycopg://...",
)
</details>

### #28921 - [docs: Fix typo in Build a Retrieval Augmented Generation Part 1 section](https://github.com/langchain-ai/langchain/pull/28921)
**Status:** 🔴 Closed  
**Author:** bengeois  
**Created:** 2024-12-25 20:00:53  
**Updated:** 2024-12-26 19:29:35  
**Labels:** lgtm, 🤖:docs, size:XS  

<details><summary>Description</summary>

This PR fixes a typo in [Build a Retrieval Augmented Generation (RAG) App: Part 1](https://python.langchain.com/docs/tutorials/rag/)
</details>

### #28882 - [Community : Add cost information for missing OpenAI model](https://github.com/langchain-ai/langchain/pull/28882)
**Status:** 🔴 Closed  
**Author:** zep-hyr  
**Created:** 2024-12-23 05:34:39  
**Updated:** 2024-12-26 19:28:32  
**Labels:** lgtm, size:XS, community  

<details><summary>Description</summary>

In the previous commit, the cached model key for this model was omitted.
When using the "gpt-4o-2024-11-20" model, the token count in the callback appeared as 0, and the cost was recorded as 0.

We add model and cost information so that the token count and cost can be displayed for the respective model.

- The message before modification is as follows.
```
Tokens Used: 0
Prompt Tokens: 0
Prompt Tokens Cached: 0 
Completion Tokens: 0  
Reasoning Tokens: 0
Successful Requests: 0
Total Cost (USD): $0.0
```

- The message after modification is as follows.
```
Tokens Used: 3783 
Prompt Tokens: 3625
Prompt Tokens Cached: 2560
Completion Tokens: 158
Reasoning Tokens: 0
Successful Requests: 1
Total Cost (USD): $0.010642500000000001
```
</details>

## Pull Requests
### #28928 - [community: add modelscope endpoint](https://github.com/langchain-ai/langchain/pull/28928)
**Status:** 🔴 Closed  
**Author:** Yunnglin  
**Created:** 2024-12-26 08:08:19  
**Updated:** 2024-12-27 02:17:47  
**Branch:** `feat/modelscope` → `master`  

<details><summary>Description</summary>

## Description

Add ModelScope inference API endpoint for both LLMs and ChatModels.

ModelScope is a leading platform to bridge model checkpoints and model applications. It offers the infrastructure for sharing open models and facilitating model-centric development (https://github.com/modelscope).


</details>

### #28924 - [partners: fix default value for stop_sequences in ChatGroq](https://github.com/langchain-ai/langchain/pull/28924)
**Status:** 🟢 Merged  
**Author:** dabzr  
**Created:** 2024-12-26 03:20:58  
**Updated:** 2024-12-26 21:43:34  
**Branch:** `patch-1` → `master`  

<details><summary>Description</summary>

- **Description:**  
      This PR addresses an issue with the `stop_sequences` field in the `ChatGroq` class. Currently, the field is defined as:
```python
stop: Optional[Union[List[str], str]] = Field(None, alias="stop_sequences")
```  
This causes the language server (LSP) to raise an error indicating that the `stop_sequences` parameter must be implemented. The issue occurs because `Field(None, alias="stop_sequences")` is different compared to `Field(default=None, alias="stop_sequences")`.  

![image](https://github.com/user-attachments/assets/bfc34cb1-c664-4c31-b856-8f18419c7350)
To resolve the issue, the field is updated to:  
```python
stop: Optional[Union[List[str], str]] = Field(default=None, alias="stop_sequences")
```  
While this issue does not affect runtime behavior, it ensures compatibility with LSPs and improves the development experience.  
- **Issue:** N/A  
- **Dependencies:** None  


</details>

### #28918 - [community: Fix error handling bug in ChatDeepInfra](https://github.com/langchain-ai/langchain/pull/28918)
**Status:** 🟢 Merged  
**Author:** andywer  
**Created:** 2024-12-25 15:41:18  
**Updated:** 2024-12-26 19:45:13  
**Branch:** `patch-1` → `master`  

<details><summary>Description</summary>

In the async ClientResponse, `response.text` is not a string property, but an asynchronous function returning a string.
</details>

### #28899 - [Update chroma.ipynb, Add langchain openai to the pip install in the chroma docs](https://github.com/langchain-ai/langchain/pull/28899)
**Status:** 🔴 Closed  
**Author:** Latticeworks1  
**Created:** 2024-12-24 04:47:37  
**Updated:** 2024-12-26 19:42:45  
**Branch:** `patch-2` → `master`  

<details><summary>Description</summary>

Description: added langchain openai to the pip
Issue: Example notebook will not run without this added
Dependencies: langchain openai

</details>

### #28909 - [Docs: Updaing 'JSON Schema' code block output](https://github.com/langchain-ai/langchain/pull/28909)
**Status:** 🟢 Merged  
**Author:** ahmadelmalah  
**Created:** 2024-12-24 23:46:03  
**Updated:** 2024-12-26 19:37:12  
**Branch:** `updating-output` → `master`  

<details><summary>Description</summary>

Out seems outdate, I ran the example several times and this is the updated output, one key-value pair was missing!
![image](https://github.com/user-attachments/assets/95231ce7-714e-43ac-b07e-57debded4735)

</details>

### #28916 - [docs: Update VectorStoreTabs.js](https://github.com/langchain-ai/langchain/pull/28916)
**Status:** 🟢 Merged  
**Author:** bongsang  
**Created:** 2024-12-25 11:04:39  
**Updated:** 2024-12-26 19:31:59  
**Branch:** `master` → `master`  

<details><summary>Description</summary>

- Title: Fix typo to correct "embedding" to "embeddings" in PGVector initialization example

- Problem: There is a typo in the example code for initializing the PGVector class. The current parameter "embedding" is incorrect as the class expects "embeddings".

- Correction: The corrected code snippet is:

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="my_docs",
    connection="postgresql+psycopg://...",
)
</details>

### #28921 - [docs: Fix typo in Build a Retrieval Augmented Generation Part 1 section](https://github.com/langchain-ai/langchain/pull/28921)
**Status:** 🟢 Merged  
**Author:** bengeois  
**Created:** 2024-12-25 20:00:53  
**Updated:** 2024-12-26 19:29:35  
**Branch:** `patch-1` → `master`  

<details><summary>Description</summary>

This PR fixes a typo in [Build a Retrieval Augmented Generation (RAG) App: Part 1](https://python.langchain.com/docs/tutorials/rag/)
</details>

### #28882 - [Community : Add cost information for missing OpenAI model](https://github.com/langchain-ai/langchain/pull/28882)
**Status:** 🟢 Merged  
**Author:** zep-hyr  
**Created:** 2024-12-23 05:34:39  
**Updated:** 2024-12-26 19:28:32  
**Branch:** `master` → `master`  

<details><summary>Description</summary>

In the previous commit, the cached model key for this model was omitted.
When using the "gpt-4o-2024-11-20" model, the token count in the callback appeared as 0, and the cost was recorded as 0.

We add model and cost information so that the token count and cost can be displayed for the respective model.

- The message before modification is as follows.
```
Tokens Used: 0
Prompt Tokens: 0
Prompt Tokens Cached: 0 
Completion Tokens: 0  
Reasoning Tokens: 0
Successful Requests: 0
Total Cost (USD): $0.0
```

- The message after modification is as follows.
```
Tokens Used: 3783 
Prompt Tokens: 3625
Prompt Tokens Cached: 2560
Completion Tokens: 158
Reasoning Tokens: 0
Successful Requests: 1
Total Cost (USD): $0.010642500000000001
```
</details>

### #28931 - [docs: add langchain dappier retriever integration notebooks](https://github.com/langchain-ai/langchain/pull/28931)
**Status:** 🟡 Open  
**Author:** amaan-ai20  
**Created:** 2024-12-26 12:32:47  
**Updated:** 2024-12-26 13:47:33  
**Branch:** `dappier-retriever` → `master`  

<details><summary>Description</summary>

Add a retriever to interact with Dappier APIs with an example notebook.

The retriever can be invoked with:

```python
from langchain_dappier import DappierRetriever

retriever = DappierRetriever(
    data_model_id="dm_01jagy9nqaeer9hxx8z1sk1jx6",
    k=5
)

retriever.invoke("latest tech news")
```

To retrieve 5 documents related to latest news in the tech sector. The included notebook also includes deeper details about controlling filters such as selecting a data model, number of documents to return, site domain reference, minimum articles from the reference domain, and search algorithm, as well as including the retriever in a chain.

The integration package can be found over here - https://github.com/DappierAI/langchain-dappier
</details>

