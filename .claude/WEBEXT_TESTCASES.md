This file includes test cases that should be inside test_recommendations_pane_suite.py

Testcase 1:
Step 1:
Go to Tools-> Add-ons, or press Ctrl+Shift+A on your keyboard
	

Expected of step 1: Recommendations tab loads.
	

Step 2:Click on an Add-on's +Add to Firefox l button.
	
Expected of step 2:
    A permission door-hanger is displayed under the left side of the URL bar with 2 buttons: Add and Cancel - check if clicking them performs the corresponding actions i.e. Add - installs add-on; Cancel - cancels the installation process.
    The Install-button disappears, being replaced with a "Manage" button - check if redirection to installed add-on detail page from add-ons manager occurs
    Add-on icon is displayed in browser toolbar
    A door-hanger containing add-on name, short info and an "Okay, Got It" button (closes the door-hanger) is displayed under the icon  

Note: ! If the add-on cannot be installed (mostly because of a faulty pref set-up)  - check if the message "Download failed. Please check your connection." together with a "Close" link are displayed

After installation add-ons are displayed in "Extensions" tab (left-side)
Check if the installed add-on is listed there and contains several options under the "three dots" menu:  

    "More Options" link - loads more details  
    "Options" button - loads more details  
    "Remove" button - check if add-on can be removed - if clicked the add-on is removed and a "Undo" option - to reverse the operation - is displayed.
    "Report" button - check if the abuse report submission form window opens.

On the left side of the "three dots" menu there's the Disable/Enable toggle button - by default the extension is enabled and the toggle button is switched on and blue.
Click on the button to switch it off - when disabled the (disable) tag will be added next to the extension's title.
Click again to switch toggle button on and enable the extension. 

Test case 2:

Step 1: Go to Tools-> Add-ons or press Ctrl+Shift+A on your keyboard
	

Expected step 1: Recommendations tab loads.


Step 2: Click on the theme's Install button.
	
Expected of step 2: Once you click on Install:

    An installation door-hanger is displayed under the left side of the URL bar with 2 buttons: Add and Cancel -check if clicking them performs the corresponding actions i.e. Add - installs the theme; Cancel - cancels the installation process  
    Theme is displayed in the browser.
    The Install button is replaced with a "Manage" button - check if redirection to installed theme detail page occurs
    A door-hanger containing add-on name, short info and an "Okay, Got It" button (closes the door-hanger) is displayed under the Hamburger Menu

 Go to the "Themes" tab and check if the installed theme is listed there and contains several options under the "three dots" menu:    

    "More Options" link - loads more details  
    "Disable" button - check if theme can be disabled  -  if clicked turns into "Enable" and the reverse action can be made.  
    "Remove" button - check if theme can be removed - if clicked the add-on is removed and a "Undo" option - to reverse the operation - is displayed.  
    "Report" button - check if the report abuse submission form window opens.

Test case 3: 


Step 1: Go to Tools-> Add-ons -> Recommendations and verify the page contents

Expected of step 1:The discovery pane page has the following info:

    A search bar

    Details about how to "Personalize Your Firefox" text with "recommends" link - check if corresponding page is loaded - https://support.mozilla.org/en-US/kb/recommended-extensions-program?as=u&utm_source=inproduct

    "Some of these recommendations are personalized..." text with "Learn more" button - check if corresponding page is loaded - https://support.mozilla.org/en-US/kb/personalized-extension-recommendations?as=u&utm_source=inproduct

    A list of add-ons and themes displayed in cassettes , each containing:

    icon for add-ons and preview for themes
    name
    author - linked to the theme or extension detail page on AMO
    add-on summary
    installation button in the right-side

    "Find more add-ons" blue button - check if AMO page is loaded

    "Privacy Policy" link loading corresponding page
