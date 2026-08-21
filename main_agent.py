# main_agent.py


from src.agent.agent import (
    run_agent
)



def main():

    print(
        "====== AI News Agent ======"
    )


    print(
        "输入 exit 退出。"
    )


    while True:

        question = input(
            "\n请输入问题: "
        )


        question = question.strip()


        if not question:

            continue


        if question.lower() == "exit":

            print(
                "退出 Agent。"
            )

            break


        try:

            answer = run_agent(
                question
            )


            print(
                "\n====== AI回答 ======"
            )


            print(
                answer
            )


        except Exception as e:

            print(
                "\nAgent运行失败:"
            )


            print(
                e
            )



if __name__ == "__main__":

    main()