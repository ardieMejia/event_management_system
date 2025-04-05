# Excel-Based-Event-Registration-Management-Python-CRUD-Application
This project is a CRUD (Create, Read, Update, Delete) or FUCK (Find, Update, Create, Kill) application for a client. Code is documentation as usual. However:

---
### If you like reading my mental shit (basically a diary jotted every day since this project started):
  1. [My Python Diary](https://github.com/ardieMejia/my-org-files/blob/main/misc/2021/PythonDiary.org): It gets better by day 20 above. But it shows every bit of exploration.
### If you want something better:
  1. [Python notes on Frameworks in org mode](https://github.com/ardieMejia/my-org-files/blob/main/misc/2025/frameworks.org): My much better written notes on Python Frameworks. It has links on popular blogs and everything. I recommend reading this and the one below if your only starting to learn Jinja. I now finally understand Django, but Jinja helps a lot if youre only starting.
  2. [General Python notes in org mode](https://github.com/ardieMejia/my-org-files/blob/main/misc/2021/Python.org): This is basic Python notes. Something I pick up here and there
### Branch details:
  * Pushed into production is tailwind_1_safe. (If Im not updating thie repo anymore, it means we're using main)
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
##### To contact me, if any question:
  * wan_ahmad_ardie@yahoo.com
##### To contribute to my efforts:
  * Im struggling with living and contributing to projects. If you believe in the importance of freelance work outside of the constraints of corporations and contributions in everything (art, writing, music). Please feel free to donate to my PayPal and be generous.
##### PayPal link:
<p>
  <a href="https://paypal.me/ardiemejia83">
      <img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="paypal">
  </a>
</p> 



