#!/usr/bin/env python

# Author:  Brian W. DeVries 
# Email:   <contingencyplan@gmail.com, brian.devries@utdallas.edu>
# License: GNU GPL v3+
# GitHub:  https://github.com/contingencyplan/grading_utilities


""" A script to make grading eLearning homework submissions more manageable by
organizing each student's submission into its own directory. See README.md in
this directory for more information.
"""


import sys
import os
import argparse
import zipfile
import re
import traceback

from submission_info.submission_info import SubmissionInfo, FormatError



# NOTE: You should not rely on any particular error having a specific code;
# for now, we keep it simple with a single code for "something went wrong."
EXIT_FAILURE = 1

PROG_DESC        = "Sanely unzips eLearning submission Zip files."


GITHUB_STR       = "https://github.com/contingencyplan/grading_utilities"
UNEXPECTED_STR   = "Unexpected error:"

ERROR_REPORT_STR = ("If this script is being run on a pristine assignment " +
                    "zip file (or this\n" +
                    "message is otherwise unexpected), then please report " +
                    "this error message to the\n" +
                    "project's GitHub page:\n" + 
                    GITHUB_STR
                   )

FERPA_STR        = ("When submitting your report, please bear in mind any " +
                    "relevant FERPA\n" +
                    "requirements.\n\n" +
                    "In particular, MAKE ABSOLUTELY SURE that your " +
                    "defect report DOES NOT contain ANY\n" +
                    "student information!!!"
                   )

FORMAT_ERROR_STR = "Formatting error in submission file: "



SUB_FILE_RE = (r"^(.*?)_" +                 # HW name up to first _
               r"([a-z]{3}\d{6})" +         # Student ID
               r"_attempt_" +               
               r"(\d{4}-\d{2}-\d{2})" +     # Date
               r"-(\d{2}-\d{2}-\d{2})" +    # Time
               r".txt$"
              )


# The default submission info filename (for extraction into the submission
# directory).
DEFAULT_SUB_INFO_FILENAME = "submission.txt"



def print_unexpected_error(ex, message = ""):
    """Print a message regarding an error that should not have occurred.

    This is used to print a message (via #sys.stderr# to the User regarding an
    exception that should not have occurred during normal / expected usage,
    followed by a recommendation to report the error via the GitHub project
    page.

    This should be used when printing an exception message that was caught but
    should not have been thrown by the program.
    
    Before printing the message from the exception #exc#, a general "unexpected
    error" message is printed, which can be overridden via #message#.

    NOTE: This does NOT exit the program; it merely prints the message to the
    User.
    """

    if len(message) == 0:
        print >> sys.stderr, UNEXPECTED_STR 
    else:
        print >> sys.stderr, message

    print >> sys.stderr, ex

    print >> sys.stderr
    
    print >> sys.stderr, ERROR_REPORT_STR

    print >> sys.stderr 
    
    print >> sys.stderr, FERPA_STR



def create_submission_directory(root, sub_info):
    """Create (as needed) a directory to contain the info for a submission.

    The directory name is returned as well.

    This will create the following directory hierarchy off of the root:

        root/
            assignment_name/
                student_name (student id)/
                    submission_date_and_time/

    If any of these directories already exist (aside from
    submission_date_and_time), then it is skipped (i.e., this situation is not
    considered an error). 
    
    Because submissions are described down to the second, it is assumed that
    no duplicate submissions exist in the assignment file. Thus, if the entire
    directory hierarchy already exists --- namely, including
    submission_date_and_time --- then the resulting #OSError# is passed to the
    caller.
     *  NOTE: If this causes problems in practice, then it can be handled
        differently, but such occurrences should be rare, and may also
        interfere with the processing of the submission attachments.

    Other #OSError#s (which, e.g., would be thrown on a failure to create the
    directory) MUST NOT be caught here, to permit the caller to decide what to
    do with them.
    """

    sub_dir = os.path.join(root, 
                           sub_info.assignment_name, 
                           sub_info.name,
                           sub_info.submission_date
                          )

    os.makedirs(sub_dir)

    return sub_dir



def extract_submission_info_file(sub_dir,
                                 assignment,
                                 sub_info_filename, 
                                 sub_info_new_filename =
                                    DEFAULT_SUB_INFO_FILENAME
                                ):
    """Extract the submission info text file into the submission directory.

    The name that the extracted file should have can be optionally provided;
    if an empty string, then the original filename is used instead.

    May throw exceptions on file creation errors, etc.
     *  TODO: Document these.
    """

    assignment.extract(sub_info_filename, sub_dir)

    current_name = os.path.join(sub_dir, sub_info_filename)
    new_name = os.path.join(sub_dir, sub_info_new_filename)

    # Rename the filename, unless the new is empty
    if sub_info_filename != "":
        os.rename(current_name, new_name)



def extract_submission_attachments(sub_dir, assignment, submission):
    """Extract the attachments for #submission# from #assignment# into
    #sub_dir#, renaming the files according to the file renaming scheme of the
    #submission#.

    According to the #zipfile# module documentation, extraction of a file
    doesn't throw any exceptions. Thanks guys! >_<
    """

    for attachment in submission.file_renames:
        assignment.extract(attachment, sub_dir)

        # Rename the file
        current_name = os.path.join(sub_dir, attachment)
        new_name = os.path.join(sub_dir, submission.file_renames[attachment])
        os.rename(current_name, new_name)



def main():
    # Set up the arg parser
    parser = argparse.ArgumentParser(description = PROG_DESC)

    # NOTE: Could possible use the argparse.FileType type information here.
    parser.add_argument("submissions_zipfile", 
                        help = "The Zip file containing the submissions."
                       )
    
    parser.add_argument("output_directory", nargs = '?', default = os.getcwd(),
                        help = "Expand the submissions into this directory " +
                               "(default: .)"
                       )
                        
    args = parser.parse_args()

    # Try opening the assignment file as a zipfile. We'll use exceptions to
    # catch if things go wrong (bad filename, not a zipfile, etc.)
    try:
        with zipfile.ZipFile(args.submissions_zipfile, 'r') as assignment:
            # Get the list of submission files from the contents of the
            # Zip file.
            sub_file_infos = [re.match(SUB_FILE_RE, f)
                                for f in assignment.namelist()
                                if re.match(SUB_FILE_RE, f)
                             ]

            # As much as we'd like to, we don't use a list comprehension here
            # so we can catch any exceptions thrown when creating a
            # SubmissionInfo object and keep going through the list.
            #
            # Presumably, errors in a single submission file should not
            # prevent the rest of the files from being unpacked; just notify
            # the User and keep going.
            #
            # TODO: Perhaps add a command-line option to prevent this.
            for sub in sub_file_infos:
                try:
                    sub_file = assignment.open(sub.string, 'rU')
                    submission = SubmissionInfo.from_file(sub_file)

                    # Create a directory to hold the submissions
                    #
                    # TODO: Handle expanding the submissions into a directory
                    # other than the current one?

                    try:
                        sub_dir = \
                                create_submission_directory(args.output_directory, 
                                                            submission
                                                           )

                        try:
                            # Extract the submission info text file into the
                            # submission directory.
                            extract_submission_info_file(sub_dir, 
                                                         assignment,
                                                         sub.string
                                                        )

                            try:
                                # Now extract the submission files into the
                                # submission directory, renaming them
                                # appropriately.
                                extract_submission_attachments(sub_dir,
                                                               assignment,
                                                               submission
                                                              )

                            # Handle errors in expanding the files
                            except OSError as os_ex:
                                # TODO: Improve this error message.
                                print >> sys.stderr, \
                                        ("Failed to expand file for\n" +
                                                sub.string + ":\n" + 
                                                os_ex.strerror + "\n\n"
                                        )

                        except OSError as os_ex:
                            print >> sys.stderr, \
                                    ("Failed to extract info file\n" + 
                                            sub.string + ":"
                                    )
                            exc_type, exc_value, _exc_tb = sys.exc_info()
                            traceback.print_exception(exc_type, 
                                                      exc_value,
                                                      _exc_tb
                                                     )
                            print >> sys.stderr, "\n\n"



                    except OSError as os_ex:
                        # TODO: We could probably improve this error message.

                        # Uncomment this line to print a traceback.
                        # traceback.print_exc()
                        print >> sys.stderr, \
                                ("Failed to create directory for\n" +
                                        sub.string + ":" 
#                                        os_ex.strerror + ": " + 
#                                        os_ex.filename + "\n\n"
                                )
                        exc_type, exc_value, _exc_tb = sys.exc_info()
                        traceback.print_exception(exc_type, 
                                                  exc_value,
                                                  None
                                                 )
                        print >> sys.stderr, "\n\n"


                # Handle formatting errors --- print a message to the User and
                # keep going
                except FormatError as fmt_ex:
                    print_unexpected_error(fmt_ex, 
                                           (FORMAT_ERROR_STR + sub.string)
                                          )


                # Something unexpected happened; print a message and keep
                # going.
                except Exception as ex:
                    # We go ahead and print a traceback in this case, as all
                    # other exception types should be handled.
                    traceback.print_exc()
                    print_unexpected_error(ex, UNEXPECTED_STR + sub)
                    
            

    # Handle any IO errors
    # TODO: We may want to handle certain errors (namely file-not-found) more
    # explicitly.
    except IOError as io_ex:
        print >> sys.stderr, "Error opening file: " + io_ex
        sys.exit(EXIT_FAILURE)

    # Handle exceptions when the input is not a zip file
    # TODO: If we decide to handle unzipped directories later, this handling
    # will not suffice.
    except zipfile.BadZipfile:
        print >> sys.stderr, "Invalid Zip file: " + args.submissions_zipfile
        sys.exit(EXIT_FAILURE)

    # Handle all other exceptions. Because we aren't expecting any other
    # exceptions here, print the "send a bug report" message.
    except Exception as ex:
        print_unexpected_error(ex)
        sys.exit(EXIT_FAILURE)



if __name__ == "__main__":
    main()


