# Package algorithms

---

Class TextComparator.py contains an algorithm with a formula for calculating the percentage of change in 
one text relative to another.
The algorithm was created as part of the task of analyzing the text how much it is necessary to change the source text
(which is written by AI) so that AI recognition systems do not recognize AI in this text.

**For example:** we will ask ChatGPT to write a text on some topic. After that, we send this text to some AI 
identification service and see, for example, the probability of AI presence in the text is 90%. After that, 
we rewrite the original text, leaving thoughts AI, in other words. We upload it to the AI identification service 
and see 10%. Great result! The last thing left to do is to understand how different the rewritten text 
was from the original one (which was written by AI). To do this, we decided to use a percentage ratio. Let's say, 
running the two above-described texts through the algorithm, we get that the text has changed by 60%. So, in order 
to reduce the probability of AI identification in the text by ~ 80%, you need to change 60% of the text.