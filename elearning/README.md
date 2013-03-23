Introduction
============

In the prior version of eLearning used at (prior to Spring 2013) included a
(somewhat hidden) feature that permitted instructors and TAs to download all
of the submissions for a particular assignment as a single Zip file. Each
student's work was placed in a separate directory containing the student's
name; most importantly (for programming assignments, at least), the original
filenames were preserved.

In the new version of eLearning, the "download all" feature is a bit easier
to find:
 1.  Click on Assignments under the Grade Center category.

 2.  Click the down arrow next to the assignment name and select "Assignment
     File Download."
      *  WARNING: Be careful to NOT click "Assignment File Cleanup," which
         is unfortunately immediately below the "Assignment File Download."
         I have not tested this functionality, so I am not certain what it
         does; however, as it refers to deleting submission files, I presume
         it does nothing good.

 3.  Click the checkbox next to the student(s) whose sumbissions you wish to
     download, or the checkbox at the top (next to "Name") to select all
     visible students.
      *  The "select all" checkbox only applies to the students currently
         visible, which may not be all students in the class. For larger
         classes, click the "Show All" button underneath the list of
         students before clicking the "select all" checkbox to download all
         submissions for the class.

 4.  Choose whether to download all submissions or only the most recent.

 5.  Click Submit and download the file that is linked on the following
     screen.


This will download a zip file containing the submissions of the selected
students. 

Unfortunately, the designers of eLearning chose a VERY poor layout for the zip
file's contents: every submitted file, for every student, is placed in the
current directory. To avoid naming collisions, the submitted filenames are
prefixed with the assignment name and the student's NetID, as well as a
submission timestamp. In addition to being a poor way to organize the
information, this automatic renaming plays havoc with programming assignments,
especially if the assignment contains multiple files (or the names of the
files are otherwise important, such as running the submission with an
automated test suite). 

Fortunately, a text file is also generated for each submission containing
the student's name and the renaming scheme used for the submitted files.
This script parses this file, creates a directory for each student and a
subdirectory for each submission, and renames the files according to this
scheme. The layout of this text file, along with a general parser for the
file, can be found in the `submission_info.py` file documentation.


Usage
=====

unpack_subs.py [-h] submissions_zipfile [output_directory]

This will load the Zip file containing the submissions and unpack them in a
sane manner into the designated output directory (defaulting to the current
directory), according to the following hierarchy:
 *  Assignment Name
 *  Student Name and ID
 *  Submission Date
 *  Submission Files

The "Assignment Name" directory must not exist in the output directory; if it
does, a warning message is printed and the program exits (to avoid overwriting
any files). The remaining directories are automatically created; because each
submission should have a unique submission time, no files should be
overwritten.


Requirements
============

 *  Python 2.7. This program makes use of the `zipfile`, `re`, and `argparse`
    modules, which are included in the standard distribution. No other
    external libraries are required.
     *  Earlier versions may work, but they are untested. 
     *  Python3 is not supported at this time.



Limitations / TODO
==================

 *  This program is written strictly for Python 2.7. Earlier versions may
    work, but no explicit support for earlier versions is planned.
 
 *  Additionally, this means that this program will not work with Python3.
    Support for Python3 (perhaps via 2to3 conversion) is planned but not
    supported at this time.

 *  The argument must be a Zip file; the script will not work with a
    collection of submissions that have already been unzipped. This seems a
    minor limitation (why would you want to unzip the file when you have this
    script? :) ), but support can be added if desired.

 *  The submission date string in the info text file begins with the day of the
    week. Currently no special processing of this string is performed, meaning
    that each submission's directory will likewise begin with the day of the
    week, which makes finding the most recent submission more difficult (as a
    simple sorting is insufficient). This will be fixed in a later update.

 *  The student name in the info text file begins with the student's first
    name; an option for "last-name-first" will be provided in a later update.

 *  To avoid the possibility of overwriting submissions, the output directory
    cannot contain a directory with the same name as the assignment. If this
    proves to be a problem, then this mechanic can be modified.

 *  This script relies on the assumption that two submissions by the same
    student MUST have unique submission times. However, this assumption has
    not been proven (e.g., an error in eLearning could permit this), but it
    seems unlikely enough that it is not handled in a more sophisticated
    manner.


License
=======

[GPL v3 or later](http://www.gnu.org/licenses/gpl.html)


Contact
=======

Bug reports (or even better, pull requests!) can be submitted at this
project's [GitHub](https://github.com/contingencyplan/grading_utilities) page.
 *  When submitting a bug report, **PLEASE** remember that we are dealing with
    student information and therefore subject to FERPA. **DO NOT EVER**
    include **any** student information in a bug report! 

The author (Brian W. DeVries) can be contacted directly at
<contingencyplan@gmail.com> and <brian.devries@utdallas.edu>.
