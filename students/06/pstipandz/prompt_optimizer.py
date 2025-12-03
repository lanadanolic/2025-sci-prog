import marimo

__generated_with = "0.18.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import json
    from google import genai

    gemini = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    STUDENT_MODEL = "gemini-2.5-flash"
    JUDGE_MODEL = "gemini-2.5-pro"

    #https://navajomathcircles.org//wp-content/uploads/2021/07/logic-puzzles.pdf Kansas State University
    logic_puzzles = [
        {
            "id": 1,
            "question": "Ispred jedne patke su dvije patke, iza jedne patke dvije patke i jedna patka u sredini. Koliko pataka ima?",
            "answer": "Tri. Dvije patke su ispred zadnje patke; prva patka ima dvije patke iza sebe; jedna patka je između druge dvije."
        },
        {
            "id": 2,
            "question": "Pet osoba jelo je jabuke. A je završio prije B, ali iza C. D je završio prije E, ali iza B. Koji je redoslijed završavanja?",
            "answer": "CABDE. A je ispred B, ali iza C → CAB. Zatim D je ispred B → CABD. E je iza D → CABDE."
        },
        {
            "id": 3,
            "question": "Čovjek ima 53 čarape u ladici: 21 plavu, 15 crnih i 17 crvenih. Mrak je i ne može vidjeti boje. Koliko čarapa mora izvaditi da bude 100% siguran da ima barem jedan par crnih?",
            "answer": "40 čarapa. Ako izvuče 21 plavu i 17 crvenih (38), još može izvući dva para prije nego bude siguran da ima barem jedan par crnih."
        },
        {
            "id": 4,
            "question": "Dan prije dva dana nakon dana prije sutra je subota. Koji je danas dan?",
            "answer": "Petak. Dan prije sutra = danas. Dan prije dva dana nakon danas = sutra. Ako je sutra subota → danas je petak."
        },
        {
            "id": 5,
            "question": "Na raskrižju si gdje jedan put vodi u Grad Laži, a drugi u Grad Istine. Osoba stoji na raskrižju, ali ne znaš odakle je. Koje pitanje trebaš postaviti kako bi saznao put do Grada Istine?",
            "answer": "\"U kojem smjeru živiš?\" Onaj iz Grada Istine govori istinu i pokazuje prema Gradu Istine; onaj iz Grada Laži laže i opet pokazuje prema Gradu Istine."
        },
        {
            "id": 6,
            "question": "Farmer želi prevesti vuka, kozu i kupus preko rijeke. Čamac može nositi samo farmera i jednu stavku. Ako ostanu zajedno vuk i koza – vuk će pojesti kozu. Ako ostanu koza i kupus – koza će pojesti kupus. Kako farmer može sve sigurno prevesti?",
            "answer": "1) Prevede kozu. 2) Vrati se sam. 3) Prevede vuka, vrati se s kozom. 4) Prevede kupus. 5) Vrati se sam. 6) Prevede kozu."
        },
        {
            "id": 7,
            "question": "Ako pet mačaka može uloviti pet miševa u pet minuta, koliko treba jednoj mački da ulovi jednog miša?",
            "answer": "Pet minuta. Svaka mačka ulovi jednog miša u istom vremenu."
        },
        {
            "id": 8,
            "question": "Postoje tri vrećice. Vrećica A sadrži dvije bijele kuglice, vrećica B dvije crne, a vrećica C jednu bijelu i jednu crnu. Nasumično izvučeš bijelu kuglicu iz nepoznate vrećice. Koja je vjerojatnost da je druga kuglica iz iste vrećice također bijela?",
            "answer": "2/3. Vrećica B otpada. Tri bijele i jedna crna kuglica ukupno → veća vjerojatnost da je vrećica A."
        }
    ]

    MAX_ITERATIONS = 10

    student_system_prompt = """
    Translate the Croatian logic puzzle into English.
    Then solve it clearly and logically.
    Format:
    Translation: ...
    Answer: ...
    """






    def student_answer(q):
        prompt = f"{student_system_prompt}\nPuzzle:\n{q}"
        resp = gemini.models.generate_content(model=STUDENT_MODEL, contents=prompt)
        return resp.text.strip()
    
    def judge_eval(student_output, answer):
        prompt = f"""
    Evaluate correctness of the student's answer.

    Correct Answer:
    {answer}

    Student Answer:
    {student_output}

    Return ONLY valid JSON with:
    {{
      "correct": true or false,
      "reason": "short justification"
    }}
    """
        try:
            resp = gemini.models.generate_content(
                model=JUDGE_MODEL,
                contents=prompt,
                config={
                    "temperature": 0.5
                }
            )

            txt = resp.text.strip()

            start = txt.find("{")
            end = txt.rfind("}")
            if start != -1 and end != -1:
                return json.loads(txt[start:end+1])
            else:
                return {"correct": False, "reason": "JSON missing"}

        except Exception as e:
            return {"correct": False, "reason": f"Judge error: {str(e)}"}

    def optimize_prompt(fails):
        prompt = f"""
    Improve this system prompt for better logical accuracy:

    Current prompt:
    {student_system_prompt}

    Failures:
    {fails}

    return ONLY the improved prompt text.
    """
        resp = gemini.models.generate_content(model=JUDGE_MODEL, contents=prompt)
        return resp.text.strip()

    for it in range(1, MAX_ITERATIONS + 1):
        print(f"\n====== ITERACIJA {it} ======")
        all_good = True
        fails = ""

        for item in logic_puzzles:
            print("\n---")
            print("Pitanje:", item["question"])

            ans = student_answer(item["question"])
            print("Student:", ans)

            eval = judge_eval(ans, item["answer"])
            print("Judge:", eval)

            if not eval["correct"]:
                all_good = False
                fails += f"\n{item['id']}: {eval['reason']}"

        if all_good:
            print("\nMODEL JE RJEŠIO ZADATAK")
            print("Iteracija:", it)
            break

        print("\nOptimiziram prompt...")
        student_system_prompt = optimize_prompt(fails)
        print("\nNovi prompt:\n", student_system_prompt)

    else:
        print("\nNema poboljšanja u maksimalnom broju iteracija")

    print("\nKRAJ\n")
    return


if __name__ == "__main__":
    app.run()
