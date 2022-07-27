from chatbot import Chat, register_call
import wikipedia
import os
import warnings
from chatbot import mapper
import functools
import json

warnings.filterwarnings("ignore")


@register_call("whoIs")
def who_is(session, query):
    try:
        return wikipedia.summary(query)
    except Exception:
        for new_query in wikipedia.search(query):
            try:
                return wikipedia.summary(new_query)
            except Exception:
                pass
    return "I don't know about " + query


def assessment(a, b, c, d, e, count, score, data):
    ret_mes = ''
    if count == 0:
        ret_mes += (
            "One of the hardest things for any financial planner to come to grips with is a client’s risk tolerance. As an investment planner, \nit is your job to translate subjective feelings into something more objective that can be used to guide the construction of an investment portfolio. Unfortunately, there is \nno standard measurement or method of assessing a client’s risk tolerance. \nA wide variety of descriptive or quantitative questionnaires are available, and you have to choose a method that works best for you.\n")

    Score = []
    questions = ['Life Stage\n1. What is your current age?',
                 '2. When do you expect to need to withdraw cash from your investment portfolio?',
                 'Financial Resources\n3. How many months of current living expenses could you cover with your present savings and liquid, \nshort-term investments, before you would have to draw on your investment portfolio?',
                 '4. Over the next few years, what do you expect will happen to your income?',
                 '5. What percentage of your gross annual income have you been able to save in recent years?',
                 '6. Over the next few years, what do you expect will happen to your rate of savings?',
                 'Emotional Risk Tolerance\n7. What are your return expectations for your portfolio?',
                 '8. How would you characterize your personality?',
                 '9. When monitoring your investments over time, what do you think you will tend to focus on?',
                 '10. Suppose you had $10,000 to invest and the choice of 5 different portfolios with a range of possible outcomes after a \nsingle year. Which of the following portfolios would you feel most comfortable investing in?',
                 '11. If the value of your investment portfolio dropped by 20% in one year, what would you do?',
                 '12. Which of the following risks or events do you fear most?'
                 ]
    selects = [['a) 65 or older',
                'b) 60 to 64.',
                'c) 55 to 59.',
                'd) 50 to 54.',
                'e) Under 50.'],
               ['a) In less than 1 year.',
                'b) Within 1 to 2 years.',
                'c) Within 2 to 5 years.',
                'd) Within 5 to 10 years.',
                'e)Not for at least 10 years'],
               ['a) Less than 3 months.',
                'b) 3 to 6 months.',
                'c) 6 to 12 months.',
                'd) More than 12 months.'],
               ['a) It will probably decrease substantially.',
                'b) It will probably decrease slightly.',
                'c) It will probably stay the same.',
                'd) It will probably increase slightly.',
                'e) It will probably increase substantially.'],
               ['a) None.',
                'b) 1 to 5%.',
                'c) 5 to 10%',
                'd) 10 to 15%',
                'e) more than 15%'],
               ['a) It will probably decrease substantially.',
                'b) It will probably decrease slightly.',
                'c) It will probably stay the same.',
                'd) It will probably increase slightly.',
                'e) It will probably increase substantially.'],
               ['a) I don’t care if my portfolio keeps pace with inflation; I just want to preserve my capital.',
                'b) My return should keep pace with inflation, with minimum volatility.',
                'c) My return should be slightly more than inflation, with only moderate volatility.',
                'd) My return should significantly exceed inflation, even if this could mean significant volatility.'],
               ['a) I’m a pessimist. I always expect the worst.',
                'b) I’m anxious. No matter what you say, I’ll worry.',
                'c) I’m cautious but open to new ideas. Convince me.',
                'd) I’m objective. Show me the pros and cons and I can make a decision and live with it.',
                'e) I’m optimistic. Things always work out in the end.'],
               ['a) Individual investments that are doing poorly.',
                'b) Individual investments that are doing very well.',
                'c) The recent results of my overall portfolio.',
                'd) The long term performance of my overall portfolio.'],
               ['a) Portfolio A, which could have a balance ranging from $9,900 to $10,300 at the end of the year.',
                'b) Portfolio B, which could have a balance ranging from $9,800 to $10,600 at the end of the year.',
                'c) Portfolio C, which could have a balance ranging from $9,600 to $11,000 at the end of the year.',
                'd) Portfolio D, which could have a balance ranging from $9,200 to $12,200 at the end of the year.',
                'e) Portfolio E, which could have a balance ranging from $8,400 to $14,000 at the end of the year.'],
               ['a) Fire my investment advisor.',
                'b) Move my money to more conservative investments immediately to reduce the potential for future losses.',
                'c) Monitor the situation, and if it looks like things could continue to deteriorate, move some of my money to more conservative investments.',
                'd) Consult with my investment advisor to ensure that my asset allocation is correct, and then ride it out.',
                'e) Consider investing more because prices are so low.'],
               ['a) A loss of principal over any period of 1 year or less.',
                'b) A rate of inflation that exceeds my rate of return over the long term, because it will erode the purchasing power of my money.',
                'c) Portfolio performance that is insufficient to meet my goals.',
                'd) Portfolio performance that is consistently less than industry benchmarks.',
                'e) A missed investment opportunity that could have yielded higher returns over the long term, even though it entailed higher risk.\nIf you want to see result, please input result to me!\n']
               ]
    # ret_mes += '\n' 提示语句有回车
    if int(count) <= 11:
        #     此时已经得到上一题答案，这次返回下一题答案
        ret_mes += str(questions[int(count)])
        ret_mes += '\n'
        select = selects[int(count)]
        for each in select:
            ret_mes += str(each)
            ret_mes += '\n'

        # print(data+'上一题接收到'+str(count))
    else:
        pass

    if count > 0:
        if data == 'a':
            a += 1
        elif data == 'b':
            b += 1
        elif data == 'c':
            c += 1
        elif data == 'd':
            d += 1
        else:
            e += 1

        if count == 1 or count == 12:
            score_cal = a * 1 + b * 2 + c * 3 + d * 4 + e * 5
            Score.append(score_cal)
            a = 0
            b = 0
            c = 0
            d = 0
            e = 0
    return ret_mes, a, b, c, d, e


def chatrobot_handle(data_str):
    chat = Chat(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Example.template"))
    first_question = ""
    # chat.converse(first_question)
    session = mapper.Session(chat, session_id="general")
    session.conversation.append_bot_message(first_question)
    callback = functools.partial(chat._say, session)
    terminate = "quit"
    input_sentence = ''
    f = open("./Chatbot/examples/info.json", 'r')
    new_dic = json.load(f)
    f.close()
    # print(new_dic['status'])
    # status=0的时候是正常，1为问卷
    #
    input_sentence = data_str
    output_sentence = ''

    if int(new_dic['status']) == 0:
        if input_sentence == 'quit':
            output_sentence = 'Bye!'
        elif input_sentence == 'assessment':
            new_dic['status'] = 1
            a = int(new_dic['a'])
            b = int(new_dic['b'])
            c = int(new_dic['c'])
            d = int(new_dic['d'])
            e = int(new_dic['e'])
            score = int(new_dic['score'])
            count = int(new_dic['count'])
            output_sentence, new_dic['a'], new_dic['b'], new_dic['c'], new_dic['d'], new_dic['e'] = assessment(a, b, c,
                                                                                                                d, e,
                                                                                                               count,
                                                                                                               score,
                                                                                                               data_str)



            pass
        else:
            output_sentence = (callback(input_sentence))
    else:
        a = int(new_dic['a'])
        b = int(new_dic['b'])
        c = int(new_dic['c'])
        d = int(new_dic['d'])
        e = int(new_dic['e'])
        score = int(new_dic['score'])
        count = int(new_dic['count'])
        if count == 0:
            count += 1
        # print('status = 1')
        # print(count,a,b,c,d,e,data_str)
        if input_sentence == 'hello':
            output_sentence = callback(input_sentence)
            new_dic['status'] = 0
            new_dic['a'] = 0
            new_dic['b'] = 0
            new_dic['c'] = 0
            new_dic['d'] = 0
            new_dic['e'] = 0
            new_dic['count'] = 0
            new_dic['score'] = 0
        else:
            output_sentence, new_dic['a'], new_dic['b'], new_dic['c'], new_dic['d'], new_dic['e'] = assessment(a, b, c,
                                                                                                                d, e,
                                                                                                               count,
                                                                                                               score,
                                                                                                               data_str)
            count += 1
            new_dic['count'] = count
            if new_dic['count'] == 13:
                new_dic['count'] = 0
                new_dic['status'] = 0
                j = a * 1 + b * 2 + c * 3 + d * 4 + e * 5
                Result = []
                if j < 11:
                    Result.append('Very conservative')
                elif j < 21:
                    Result.append('Moderately conservative')
                elif j < 31:
                    Result.append('Moderate')
                elif j < 41:
                    Result.append('Moderately Aggressive')
                else:
                    Result.append('Very aggressive')
                output_sentence = 'Your Investment Style is: \n\r' + str(Result[0]) + output_sentence
            elif count == 2 + 1:
                i = a * 1 + b * 2 + c * 3 + d * 4 + e * 5
                Result = []
                if i <= 3:
                    Result.append('Short-term (5 years or less)')
                elif i <= 6:
                    Result.append('Intermediate-term (5 to 10 years)')
                else:
                    Result.append('Long-term (over 10 years)')
                output_sentence = 'Your Investment Time Horizon is: \n\r' + str(Result[0]) + '\n' + output_sentence

            # output_sentence = assessment()

    f = open('./Chatbot/examples/info.json', 'w')
    json.dump(new_dic, f)
    f.close()
    return output_sentence



# print("hello")
# print((chatrobot_handle("hello")))
# print("ass")
# print(chatrobot_handle("assessment"))
# for i in range(2):
#     print('a')
#     print(chatrobot_handle("a"))
# print('hello')
# print(chatrobot_handle("hello"))
# print('assess')
# print(chatrobot_handle("assessment"))
# print("hello")
# print(chatrobot_handle("hello"))
