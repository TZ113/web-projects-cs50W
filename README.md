# CABINET
#### Video Demo: <https://youtu.be/vn8bM4vKAbw>
#### Description:

It's a web application for uploading and storing files. Users can create accounts by registering here. Then they can upload certain kinds of files, namely, the popular formats for audio, video, image, documents etc can be uploaded here. Then these files will be stored to be downloaded and/or deleted later. The users can change their passwords or E-mail addresses later whenever they want, they can also delete their accounts as well.

For the server side I've used flask, for templating jinja2 and on the client side javascript and jquery. For jquery and javascript I've used several jquery libraries. All the server side code is contained in one file, the app.py. Maybe I should've used two. The required python libraries are listed in the requirements.txt file. There is a single sql database named files.db which contains two tables - users and files. The users table contains all the user information and information about the uploaded files are stored in the files table. The upload directory is contained in the static folder, where subdirectories with names corresponding to the user-ids are created dynamically when the user account is created, then each individual users files are uploaded to and stored in those directories. Files are uploaded using ajax post requests. I've used bootstrap 4.5.3 library for styling as well as the styles.css for additional styling which is contained in the static folder.




 All the templates are contained in the templates directory
 - layout.html is the base template
 - apology.html is rendered to return apology to the user.
 - register.html is rendered for registering the user. There's a token verification system that sends a token to the e-mail address provided by the user which the user needs confirm to create the account. Then verify_email.html is rendered to get the token that was sent to the e-mail address as input to verify and then register the user
 - login.html is rendered for logging the user in, obviously
 - index.html is rendered as default page once the user is logged in. The uploaded files are displayed as a table on the index page with informations like filesize and time of upload as well as their names. Users can download and/or delete files directly from the index. They have to be downloaded or deleted individually as well. Users can select to display files by their category, which are audio, video, image, document and others. Users can also sort them by their name,in ascending or descending order, by size, and finally, by their time of upload. Ajax post requests are used for these functionalities.
- upload.html is rendered when the user clicks the upload button, it provides the uploading functionality. Only files with the following extensions will be allowed to be uploaded: - ".txt, .doc, .pdf, .epub, .rtf, .png, .jpeg, .jpg, .gif, .bmp, .mp3, .wav, .m4a, .aac, .flac, .wma, .mp4, .avi, .mkv, .flv and .zip". Files can be uploaded one at a time and file size has to be within 100.00Mb, if the size of a file that the user wishes to upload exceeds the maximum allowed size then an alert message appears to notify the user. And also, if there's an already existing file with the name of the file the user wishes to upload a prompt appears to ask the user whether he/she wishes to replace the existing file with the new one.
- change_psswd_check.html and change_psswd.html are rendered if the user wishes to change the password. change_psswd_check.html is used to confirm the user's current password and then change_psswd.html to update the database with the new password.
- and finally, change_email_psswd_check.html and change_email.html are for changing the e-mail address.
