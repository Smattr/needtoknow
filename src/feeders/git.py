import base
import cStringIO, os, shutil, subprocess, tarfile, tempfile

def run(cmd, cwd):
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return p.returncode, stdout.strip(), stderr.strip()

class Feeder(base.Feeder):

    def __iter__(self):
        for n, i in self.feeds.items():

            assert 'url' in i
            remote = i['url']

            branch = i.get('branch', 'master')

            state = self.resource.get((remote, branch))

            # Create a temporary directory to work in.
            tmp = tempfile.mkdtemp()

            if state is None:
                # This is the first time we've encountered this repository. We
                # need to clone it.
                ret, _, stderr = run(['git', 'clone', '--bare', '--branch',
                    branch, remote, '.'], tmp)
                if ret != 0:
                    yield Exception('failed to clone %(url)s:\n%(err)s' % {
                            'url':remote,
                            'err':stderr,
                        })
                    shutil.rmtree(tmp)
                    continue

                last_commit = None

            else:
                # We have a previous working directory for this repository. We
                # need to extract it.
                last_commit, data = state

                buffer = cStringIO.StringIO(data)
                with tarfile.open(fileobj=buffer) as t:
                    t.extractall(tmp)

                # Update the history in the working directory.
                ret, _, stderr = run(['git', 'fetch', remote, '%s:%s' %
                    (branch, branch)], tmp)
                if ret != 0:
                    yield Exception('failed to update temporary working '
                        'directory for %(url)s:\n%(err)s' % {
                            'url':remote,
                            'err':stderr,
                        })
                    shutil.rmtree(tmp)
                    continue

            # Now retrieve the log and look for new commits.
            ret, stdout, stderr = run(['git', 'log', '--reverse', '--pretty=%H',
                branch], tmp)
            if ret != 0:
                yield Exception('failed to retrieve Git log of '
                    '%(url)s:\n%(err)s' % {
                        'url':remote,
                        'err':stderr,
                    })
                shutil.rmtree(tmp)
                continue

            # Look for any new commits to this branch.
            seen_last_commit = False
            for commit in stdout.splitlines():

                if last_commit is None or seen_last_commit:
                    # This is a new commit.

                    ret, summary, stderr = run(['git', 'log', '-n', '1',
                        '--format=%s', commit], tmp)
                    if ret != 0:
                        yield Exception('failed to retrieve summary for Git '
                            'commit %(commit)s of %(url)s:\n%(err)s' % {
                                'commit':commit,
                                'url':remote,
                                'err':stderr,
                            })
                        continue

                    ret, diff, stderr = run(['git', 'show', commit], tmp)
                    if ret != 0:
                        yield Exception('failed to retrieve diff for Git '
                            'commit %(commit)s of %(url)s:\n%(err)s' % {
                                'commit':commit,
                                'url':remote,
                                'err':stderr,
                            })
                        continue

                    yield base.Entry(n, summary, diff)

                    last_commit = commit
                    seen_last_commit = True

                elif commit == last_commit:
                    seen_last_commit = True

            # Tar up the working directory to store in our resources. We don't
            # bother compressing it because the resources as a whole are
            # compressed.
            buffer = cStringIO.StringIO()
            with tarfile.open(fileobj=buffer, mode='w') as t:
                for item in os.listdir(tmp):
                    path = os.path.join(tmp, item)
                    t.add(path, item)
            data = buffer.getvalue()

            shutil.rmtree(tmp)

            self.resource[(remote, branch)] = (last_commit, data)
