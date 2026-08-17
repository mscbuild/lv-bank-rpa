from pathlib import Path
from tempfile import NamedTemporaryFile


class AtomicFileWriter:

    @staticmethod
    def write(
        destination: Path,
        content: bytes,
    ) -> None:

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            delete=False,
            suffix=".tmp",
        ) as temporary:

            temporary.write(content)
            temporary.flush()

            temporary_path = Path(
                temporary.name
            )

        temporary_path.replace(destination)
