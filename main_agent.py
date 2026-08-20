from src.agent.agent import run_agent



while True:


    q=input(
        "\n请输入问题:"
    )


    if q=="exit":
        break



    answer=run_agent(q)


    print(
        "\n======回答======"
    )


    print(answer)