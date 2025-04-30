# Event-Registration-Management-Python-CRUD-Application
1. 2 models: Member and Event
2. Still a work in progress
3. Flask + Tailwind CSS + PostgreSQL
4. A CRUD (Create, Read, Update, Delete) or FUCK (Find, Update, Create, Kill) based project application, working prototype for Malaysian Chess Federation
5. Code is documentation as usual. However:

---
### Personal Notes:
  1. [My Python Diary](https://github.com/ardieMejia/my-org-files/blob/main/misc/2021/PythonDiary.org): gradual writing since day 1.
  2. [Python notes on Frameworks in org mode](https://github.com/ardieMejia/my-org-files/blob/main/misc/2025/frameworks.org): Links and writings on frameworks in general
  3. [General Python notes in org mode](https://github.com/ardieMejia/my-org-files/blob/main/misc/2021/Python.org): Notes on Python in general. The many peculiar tricks one can do in Python (List comprehension, etc..)
### Branch details:
  * Pushed into production is tailwind_1_safe.
>>>>>>> tailwind_1_safe
### To run details:
  * flask --app main.py run --debug --extra-files "templates/form.html:crud.py:main.py"
  #### I use this trick with --extra-files
  * flask run --debug --extra-files $(extra_f)
  * where extra_f is a function from Bash
  ```
  function extra_f {
	  local extra_f_var=`cat $(pwd)'/temp_extra_files.txt'`
	  echo ${extra_f_var}
}
  ```

  * Example of temp_extra_files.txt contains files that need watching like:
  ```
  app.py:config.py:model.py:wsgi.py:xlsx2csv.py:./templates/base_form_h.html
 ```
##### To contact me, if any question:
  * wan_ahmad_ardie@yahoo.com
##### My other links:
<p>My YouTube channel: 
  <a href="https://www.youtube.com/@ArdieMejia83">
      <img width="100" src="https://static.cdnlogo.com/logos/y/92/youtube.svg" alt="YouTube">
  </a>
</p> 
##### To contribute to my efforts:
  * Im not just a programmer, I do piano interpretations and Emacs exploration. If you believe in the importance of freelance work outside of just corporation constraint including art, writing and music. Please feel free to donate to my PayPal and be generous.## Heading

##### PayPal link:
<p>
  <a href="https://paypal.me/ardiemejia83">
      <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="paypal">
  </a>
</p> 




