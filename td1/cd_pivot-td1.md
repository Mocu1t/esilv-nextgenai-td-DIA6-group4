# TD 1 - models x questions

| model | nature | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 | C19 | C20 | correct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| groq:openai/gpt-oss-120b | real | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | WRONG | OK | OK | OK | 19/20 |
| groq:openai/gpt-oss-20b | real | OK | WRONG | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | 19/20 |
| openrouter:cohere/north-mini-code:free | real | OK | WRONG | OK | OK | OK | OK | OK | WRONG | WRONG | INV | WRONG | OK | OK | OK | OK | OK | WRONG | OK | WRONG | OK | 13/20 |
| groq:qwen/qwen3.8-27b | real | OK | OK | OK | OK | OK | OK | OK | OK | WRONG | OK | OK | OK | OK | OK | WRONG | WRONG | WRONG | OK | WRONG | N/E | 14/20 |
| openrouter:dots-studio/dots-3-note-preview:free | real | OK | WRONG | OK | OK | OK | OK | INV | WRONG | WRONG | OK | WRONG | OK | OK | OK | WRONG | WRONG | OK | WRONG | OK | OK | 12/20 |

OK correct, WRONG incorrect value, INV invalid SQL, REJ rejected by sandbox, ACC access error, N/E not executed.
Source: model-question-comparison-en.csv (last attempt per cell); raw attempts in traces-td1.csv.


Question types: C01 period; C02 age on a reference date; C03 product list; C04 period; C05 period; C06 period; C07 period; C08 age on a reference date; C09 age on a reference date; C10 age at the time of the order; C11 age on a reference date; C12 product list; C13 product list; C14 product list; C15 period + age on a reference date; C16 age on a reference date + product list; C17 period + age on a reference date + product list; C18 period + age at the time of the order; C19 period + age on a reference date + product list; C20 period
