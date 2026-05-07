from langchain.prompts import PromptTemplate


class RAGPrompt(object):
    @staticmethod
    def rag_prompt():
        prompt = PromptTemplate(
            input_variables=["context", "question", "phone"],
            template="""  
            你是一个智能助手，帮助用户回答问题。  
            如果提供了上下文，请基于上下文回答；如果没有上下文，请直接根据你的知识回答。  
            如果答案来源于检索到的文档，请在回答中说明。

            上下文: {context}  
            问题: {question}  

            如果无法回答，请回复：“信息不足，无法回答，请联系人工客服，电话：{phone}。”  
            回答:  
            """,
        )
        return prompt

    # 定义假设问题生成的 Prompt 模板
    @staticmethod
    def hyde_prompt():
        #   创建并返回 PromptTemplate 对象
        return PromptTemplate(
            template="""  
            假设你是用户，想了解以下问题，请生成一个简短的假设答案：  
            问题: {query}  
            假设答案:  
            """,
            #   定义输入变量
            input_variables=["query"],
        )

    #   定义子查询生成的 Prompt 模板
    @staticmethod
    def subquery_prompt():
        #   创建并返回 PromptTemplate 对象
        return PromptTemplate(
            template="""  
            将以下复杂查询分解为多个简单子查询，每行一个子查询：  
            查询: {query}  
            子查询:  
            """,
            #   定义输入变量
            input_variables=["query"],
        )

    #   定义回溯问题生成的 Prompt 模板
    @staticmethod
    def backtracking_prompt():
        #   创建并返回 PromptTemplate 对象
        return PromptTemplate(
            template="""  
            将以下复杂查询简化为一个更简单的问题：  
            查询: {query}  
            简化问题:  
            """,
            #   定义输入变量
            input_variables=["query"],
        )


if __name__ == '__main__':
    # prompt = RAGPrompt.rag_prompt()
    # result = prompt.format(context="你知道大模型吗", question="你猜一下", phone="12345678")
    # print(f"result===========>{result}")
    hyde = RAGPrompt.hyde_prompt()
    print(hyde.format(query="你知道大模型吗"))
