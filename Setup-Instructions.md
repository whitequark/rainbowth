## Starting
This is a sample code being used to show what the setup process is like. At this moment, nothing is set up.
![Step-1](img/1.png)

## Install package control
If you do not have package control installed, install it from the `Command Palette` (`Cmd`+`Shift`+`p` on macOS, `Ctrl`+`Shift`+`p` elsewhere):
![Step-2](img/2.png)

## Install Rainbowth package
Using the command palette, install the `Rainbowth` package:
![Step-3](img/3.png)
![Step-4](img/4.png)

## Browse packages
You can visit your packages by going to *Preferences > Browse Packages...*:
![Step-5](img/5.png)
![Step-6](img/6.png)
![Step-7](img/7.png)

## Install a color theme
For our example, we are going to install the *Dracula theme*.
![Step-8](img/8.png)
![Step-9](img/9.png)

## Set to the installed theme
![Step-10](img/10.png)
![Step-11](img/11.png)

## Install PackageResourceViewer
In order for Rainbowth to be able to edit the themes to color the text, we will have to create the theme files in the *Packages* folder. This can be easily done using a package called **PackageResourceViewer**.
![Step-12](img/12.png)
![Step-13](img/13.png)

## Extract theme files
Using PackageResourceViewer, extract the relevant files for the theme (in our case, the *Dracula* theme):
![Step-14](img/14.png)
![Step-15](img/15.png)

This will create the files related to the theme in *Packages* folder. The folder should look somewhat like this now:
![Step-16](img/16.png)

## Rainbowth.sublime-settings
Create a `Rainbowth.sublime-settings` in `User`:
![Step-17](img/17.png)

Now, edit the file with languages and colors you want to use:
![Step-18](img/18.png)

## Success
The changes should apply automatically, if not, quit Sublime and open it again to see Rainbowth working.
![Step-19](img/19.png)
