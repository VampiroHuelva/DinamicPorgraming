#!/usr/bin/python3

"""Template for dynamic programming assignment.

The code in the template is compatible with both Python 2 and Python 3
When you finish this code, it should be at least compatible with Python 3.
"""

# Packages for commandline options:
import argparse
import sys
import pickle as pk

## Initialice score Matrix

M = []
sequences = ""
# Built-in exchange matrices.
with open('substitution_matrices/identity.pkl', 'rb') as f:
    identity = pk.load(f)

with open('substitution_matrices/pam250.pkl', 'rb') as f:
    pam250 = pk.load(f)

with open('substitution_matrices/blosum62.pkl', 'rb') as f:
    blosum62 = pk.load(f)


def get_args():
    """Collect the inputs."""
    parser = argparse.ArgumentParser(
        prog='PROG',
        usage='%(prog)s [options]',
        description='Aligning two sequences',
        epilog='The code was co-opted from Anton Feenstra\'s and'
               'modified by Cico Zhang'
    )
    parser.add_argument('-f', '--fasta', dest='fasta', metavar='FILE',
                        required=True, help='input alignment file (fasta)')
    parser.add_argument('-e,', '--exchange_matrix', dest='exchange_matrix',
                        metavar='SUBSTITUTION MATRIX NAME', help='Substitution '
                                                                 'matrix: pam250, blosum62 or identity',
                        default='pam250')
    parser.add_argument('-l', '--local', dest='align_local',
                        action='store_true', help='Local alignment',
                        default=False)
    parser.add_argument('-g', '--global', dest='align_global',
                        action='store_true', help='Global alignment',
                        default=False)
    parser.add_argument('-s', '--semi_global', dest='align_semiglobal',
                        action='store_true', help='Semi-global alignment',
                        default=False)
    parser.add_argument('-p', '--penalty', dest='gap_penalty', type=int,
                        help='Gap penalty', default=2)
    parser.add_argument('-o', '--output', dest='alignment', metavar='FILE',
                        default='output.align', help='The file to store the alignment')
    parser.add_argument('-m', '--score_matrix', dest='score_matrix',
                        metavar='FILE', default='output.align',
                        help='The file to store the score matrix')
    parser.add_argument('-v', dest='print_on_screen', action='store_true',
                        help='Print the output (alignment(s) and score '
                             'matrix) on the screen', default=False)

    args = parser.parse_args()

    if args.fasta is None:
        sys.exit('Error: no input file (fasta)')

    if not (args.align_local or args.align_global or args.align_semiglobal):
        sys.exit('Error: No alignment strategy is given: global, local or '
                 'semi-global')
    if args.align_local + args.align_global + args.align_semiglobal > 1:
        sys.exit('Error: More than one alignment strategy is given.')

    if args.exchange_matrix not in ['pam250', 'blosum62', 'identity']:
        sys.exit('Unknown exchange matrix ' + args.exchange_matrix)

    return args


class Sequence:
    """Stores a sequence object."""

    def __init__(self, Label="", Sequence=""):
        """Initialize a new Sequence object.

        Label -- identifier of sequence (text)
        Sequence -- sequence string in single-letter alphabet
        """
        self.Label = Label
        self.Sequence = Sequence

    # this makes that you can do 'print sequence' and get nice output:
    def __str__(self):
        """Return string representation of a Sequence object."""
        # newline-delimited values of all the attributes
        return ">%s\n%s" % (self.Label, self.Sequence)


def readSequences(lines):
    """Return Sequences object.

    lines -- list of lines or any object that behaves like it

    This routine parses a fasta file and returns a list of Sequence objects
    containing the sequences with label and sequence data set
    """
    seqs = []
    label = None
    seq_lines = []
    for line in lines:
        line = line.strip()  # strip off white space
        if not line:  # skip empty lines
            continue
        if line.startswith(';'):  # ignore comment lines
            continue
        # check for start of next sequence:
        if line.startswith('>'):  # label line
            # first, store the previous sequence if we had one:
            if seq_lines:
                seqs.append(Sequence(label, ''.join(seq_lines)))
                seq_lines = []
            # get the label (name) for the next sequence
            label = line[1:].strip()
        else:
            # collect all lines with sequence information for this sequence:
            seq_lines.append(line)
    # take care of the last sequence in the file
    seqs.append(Sequence(label, ''.join(seq_lines)))
    return seqs


def do_global_alignment(sequences, matrix, penalty):
    """Do pairwise global alignment using DP."""
    #########################
    # INSERT YOUR CODE HERE #
    #########################
    for i in range(0, len(sequences[0].Sequence) + 1):

        for j in range(0, len(sequences[1].Sequence) + 1):
            if i == 0 or j == 0:
                M[i][j] = (i * (-penalty)) + (j * (-penalty))
            else:
                M[i][j] = max(M[i - 1][j - 1] + matrix[ord(sequences[0].Sequence[i - 1]) - ord("A")][
                    ord(sequences[1].Sequence[j - 1]) - ord("A")],
                              M[i - 1][j] - penalty, M[i][j - 1] - penalty)

        ## Alingment
        # ni and nj been the position of the alignment in each string
    ni = len(sequences[0].Sequence) - 1
    nj = len(sequences[1].Sequence) - 1
    # Create the alignmnet list of lists
    ali = [[""], [""], [""], [""]]
    while (ni >= 0 or nj >= 0):
        mat = matrix[ord(sequences[0].Sequence[ni]) - ord("A")][ord(sequences[1].Sequence[nj]) - ord("A")]
        if (M[ni + 1][nj + 1] == M[ni][nj] + mat):
            ali[0].insert(0, sequences[0].Sequence[ni])
            ali[2].insert(0, sequences[1].Sequence[nj])
            if (sequences[0].Sequence[ni] == sequences[1].Sequence[nj]):
                ali[1].insert(0, "|")
            else:
                ali[1].insert(0, " ")
            ni = ni - 1
            nj = nj - 1

        # check if we came from above
        elif (M[ni + 1][nj + 1] == M[ni][nj + 1] - penalty):
            ali[0].insert(0, sequences[0].Sequence[ni])
            ali[1].insert(0, " ")
            ali[2].insert(0, "-")
            ni = ni - 1
        # Could use just else, because there are only 3 options of where to came. But with it I can check if its all oK
        elif (M[ni + 1][nj + 1] == M[ni + 1][nj] - penalty):
            ali[0].insert(0, "-")
            ali[1].insert(0, " ")
            ali[2].insert(0, sequences[1].Sequence[nj])
            nj = nj - 1

    score = M[len(sequences[0].Sequence)][len(sequences[1].Sequence)]
    ali[3] = ("score = " + str(score))
        # else:
    score = M[len(sequences[0].Sequence)][len(sequences[1].Sequence)]
    # print ("ERROR; The score Matrix is wrong")
    return ali,M


    #########################
    #   END YOUR CODE HERE  #
    #########################


def do_local_alignment(sequences, matrix, penalty):
    """Do pairwise local alignment using DP."""
    #########################
    # INSERT YOUR CODE HERE #
    #########################
    max_score = 0
    # first row and column do not need to be computed, just 0.
    for i in range(1, len(sequences[0].Sequence) + 1):

        for j in range(1, len(sequences[1].Sequence) + 1):

            M[i][j] = max(M[i - 1][j - 1] + matrix[ord(sequences[0].Sequence[i - 1]) - ord("A")][
                ord(sequences[1].Sequence[j - 1]) - ord("A")],
                          M[i - 1][j] - penalty, M[i][j - 1] - penalty)
            if (M[i][j] < 0):
                M[i][j] = 0
            if (M[i][j] >= max_score):
                max_score = M[i][j]
                max_i = i
                max_j = j

    # The alignment is extended from the highest scoring point to 0

    ni = max_i - 1
    nj = max_j - 1
    # Create the alignmnet list of lists
    ali = [[""], [""], [""], [""]]
    while (M[max_i][max_j] > 0):
        mat = matrix[ord(sequences[0].Sequence[ni]) - ord("A")][ord(sequences[1].Sequence[nj]) - ord("A")]

        if (M[max_i][max_j] == M[max_i - 1][max_j - 1] + mat):
            ali[0].insert(0, sequences[0].Sequence[ni])
            ali[2].insert(0, sequences[1].Sequence[nj])
            if (sequences[0].Sequence[ni] == sequences[1].Sequence[nj]):
                ali[1].insert(0, "|")
            else:
                ali[1].insert(0, " ")
            max_i = max_i - 1
            ni = ni - 1
            max_j = max_j - 1
            nj = nj - 1

        # check if we came from above
        elif (M[max_i][max_j] == M[max_i - 1][max_j] - penalty):
            ali[0].insert(0, sequences[0].Sequence[ni])
            ali[1].insert(0, " ")
            ali[2].insert(0, "-")
            max_i = max_i - 1
            ni = ni - 1
        # Could use just else, because there are only 3 options of where to came. But with it I can check if its all oK
        elif (M[max_i][max_j] == M[max_i][max_j - 1] - penalty):
            ali[0].insert(0, "-")
            ali[1].insert(0, " ")
            ali[2].insert(0, sequences[1].Sequence[nj])
            max_j = max_j - 1
            nj = nj - 1

    ali[3] = ("score = " + str(max_score))

    return ali, M

    #########################
    #   END YOUR CODE HERE  #
    #########################


def do_semiglobal_alignment(sequences, matrix, penalty):
    """Do pairwise semi-global alignment using DP."""
    #########################
    # INSERT YOUR CODE HERE #
    #########################
    ## Score matrix calculation
    max_score = 0
    for i in range(1, len(sequences[0].Sequence) + 1):

        for j in range(1, len(sequences[1].Sequence) + 1):
            M[i][j] = max(M[i - 1][j - 1] + matrix[ord(sequences[0].Sequence[i - 1]) - ord("A")][
                ord(sequences[1].Sequence[j - 1]) - ord("A")],
                          M[i - 1][j] - penalty, M[i][j - 1] - penalty)
            if (i == len(sequences[0].Sequence) or j == len(sequences[1].Sequence)):
                if (M[i][j] >= max_score):
                    max_score = M[i][j]
                    max_i = i
                    max_j = j





####comparing
    ni = len(sequences[0].Sequence) - 1
    nj = len(sequences[1].Sequence) - 1
    # Create the alignmnet list of lists
    ali = [[""], [""], [""], [""]]
    while (ni >= 0 or nj >= 0):
        mat = matrix[ord(sequences[0].Sequence[ni]) - ord("A")][ord(sequences[1].Sequence[nj]) - ord("A")]
        if (M[ni + 1][nj + 1] == M[ni][nj] + mat):
            ali[0].insert(0, sequences[0].Sequence[ni])
            ali[2].insert(0, sequences[1].Sequence[nj])
            if (sequences[0].Sequence[ni] == sequences[1].Sequence[nj]):
                ali[1].insert(0, "|")
            else:
                ali[1].insert(0, " ")
            ni = ni - 1
            nj = nj - 1

        # check if we came from above
        elif (M[ni + 1][nj + 1] == M[ni][nj + 1] - penalty):
            ali[0].insert(0, sequences[0].Sequence[ni])
            ali[1].insert(0, " ")
            ali[2].insert(0, "-")
            ni = ni - 1
        # Could use just else, because there are only 3 options of where to came. But with it I can check if its all oK
        elif (M[ni + 1][nj + 1] == M[ni + 1][nj] - penalty):
            ali[0].insert(0, "-")
            ali[1].insert(0, " ")
            ali[2].insert(0, sequences[1].Sequence[nj])
            nj = nj - 1


    ali[3] = ("score = " + str(max_score))
        # else:
    score = M[len(sequences[0].Sequence)][len(sequences[1].Sequence)]
    # print ("ERROR; The score Matrix is wrong")
    return ali,M



#########################
    #   END YOUR CODE HERE  #
    #########################


def print_matrix_to_file(matrix, fileName):
    """Write a matrix into file.

    matrix: a list of list in Python, storing a score
    matrix.
    fileName: str, a file name (with a path) to store the matrix.
    It is not recommended to tinker with this function.
    """
    with open(fileName, 'w') as f:
        for row in matrix:
            print('\t'.join(map(str, row)), file=f)


def print_alignment_to_file(alig, fileName):
    """Write a matrix into file.

    alig: a list of list in Python, storing an alignment.
    fileName: str, a file name (with a path) to store the alignment.
    It is not recommended to tinker with this function.
    """
    with open(fileName, 'w') as f:
        for row in alig:
            print(''.join(map(str, row)), file=f)


def print_matrix_on_screen(matrix, width=5):
    """Print a matrix on the screen.

    matrix: a list of list in Python, storing an alignment or a score
    matrix.
    width: that of the space one cell occupies.
    This will facilitate your testing.
    """
    for row in matrix:
        print(''.join(['{0:>{w}}'.format(item, w=width) for item in row]))


def main():
    """Main function.

    Please change it accordingly to make the program work.
    """
    # Get command line options
    args = get_args()


    # Set substitution matrix:
    if args.exchange_matrix == "pam250":
        exchangeMatrix = pam250
    elif args.exchange_matrix == "blosum62":
        exchangeMatrix = blosum62
    else:
        exchangeMatrix = identity

    # Read sequences from fasta file, and catch error reading file
    try:
        sequences = readSequences(open(args.fasta))
    except OSError as e:
        print("ERROR: cannot open or read fasta input file:", e.filename)

    for seq in sequences:
        print(seq)

    # Initialise ascore matrix(M) with real dimnesion but 0 values
    for i in range(0, len(sequences[0].Sequence) + 1):
        M.append([0] * (len(sequences[1].Sequence) + 1))

    # Call alignment routine(s):
    if args.align_global:
        alignment, score_matrix = do_global_alignment(
            sequences, exchangeMatrix, args.gap_penalty)
    elif args.align_local:
        alignment, score_matrix = do_local_alignment(
            sequences, exchangeMatrix, args.gap_penalty)
    elif args.align_semiglobal:
        alignment, score_matrix = do_semiglobal_alignment(
            sequences, exchangeMatrix, args.gap_penalty)
    else:
        sys.exit("BUG! this should not happen.")


    #I have decided to add here(on main function) the sequences to the score matrix  instead of doing it inside each
    # function so is more eficient

    # Conversion of Sequence string to a list of strings
    Seq_list1 = list(sequences[0].Sequence)
    Seq_list2 = list(sequences[1].Sequence)
    Seq_list1.insert(0, "-")
    Seq_list2.insert(0, "-")

    # Add Seq_list1 as the first column
    n_Seq_list1 = 0
    for lista in score_matrix:
        lista.insert(0, Seq_list1[n_Seq_list1])
        n_Seq_list1 = n_Seq_list1 + 1

    # Add Seq_list2 as the first row
    score_matrix.insert(0, Seq_list2)
    score_matrix[0].insert(0, "")



    # Print the result to files
    if args.alignment:
        print_alignment_to_file(alignment, args.alignment)
    if args.score_matrix:
        print_matrix_to_file(score_matrix, args.score_matrix)

    # Print the result on screen
    if args.print_on_screen:
        print("\n")
        print("<-------------ALIGNMENT-------------->")
        print("\n")
        print_matrix_on_screen(alignment)
        print("\n")
        print("<-------------SCORE MATRIX-------------->")
        print("\n")
        print_matrix_on_screen(score_matrix)


if __name__ == "__main__":
    main()

# last line
