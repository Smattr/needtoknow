def suppress_whitespace(lines):
    '''
    Remove hunks from a unified diff that only contain white space changes.
    '''

    # States for following state machine.
    IDLE, IN_HUNK = list(range(2))

    # Initial state. Note that we only accumulate lines in IN_HUNK.
    state = IDLE
    accumulated = None

    for line in lines:

        if state == IDLE:
            assert accumulated is None

            if line.startswith('@@'):
                # Encountered a new hunk.
                accumulated = [line]
                state = IN_HUNK

            else:
                # Unknown line. Note that we end up here if we're within a hunk
                # that we've already decided to keep.
                yield line

        else:
            assert state == IN_HUNK
            assert isinstance(accumulated, list)

            if (line.startswith('+') or line.startswith('-')) and \
                    line[1:].strip() != '':
                # This is a non-empty change line. Decide to keep this hunk.
                for a in accumulated:
                    yield a
                accumulated = None
                state = IDLE

            elif line.startswith('@@'):
                # Encountered a new hunk without finding anything interesting in
                # the current hunk. Ditch the current hunk (the prior contents
                # of `accumulated`.
                accumulated = [line]

            else:
                # Haven't decided whether to keep this hunk yet.
                accumulated.append(line)
