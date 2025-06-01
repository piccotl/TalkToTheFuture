from app.cli import TalkToTheFutureCLI

if __name__ == "__main__":
    cli = TalkToTheFutureCLI(trace_level='WARNING')
    cli.run()