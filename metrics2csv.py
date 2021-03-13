import argparse
import re
import xml.etree.ElementTree as Etree
from typing import List


class Value:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "")
        self.source: str = kwargs.get("source", "")
        self.package: str = kwargs.get("package", "")
        self.value: str = kwargs.get("value", "")
        self.in_range: str = kwargs.get("inrange", "")


class Stats:
    def __init__(self, **kwargs):
        self.per: str = kwargs.get("per", "")
        self.avg: str = kwargs.get("avg", "")
        self.stddev: str = kwargs.get("stddev", "")
        self.max: str = kwargs.get("max", "")
        self.total: str = kwargs.get("total", "")
        self.max_in_range: str = kwargs.get("maxinrange", "")


class Metric:
    def __init__(self, **kwargs):
        # TODO: don't forget scope!
        self.id: str = kwargs.get("id", "")
        self.description: str = kwargs.get("description", "")
        self.max: str = kwargs.get("max", "")
        self.min: str = kwargs.get("min", "")
        self.hint: str = kwargs.get("hint", "")
        self.scope: str = kwargs.get("scope", "")
        self.stats: Stats = Stats()

        self._values: List[Value] = list()

    def with_stats(self, stats: Stats):
        self.stats = stats

    def with_values(self, values: List[Value]):
        self._values.extend(values)

    def as_csv(self) -> List[str]:
        return [
            "{};{};{}\n".format(
                self._metrics_info_as_line(),
                self._stats_as_line(),
                self._value_as_line(v)
            )
            for v in self._values
        ]

    @staticmethod
    def _value_as_line(value: Value):
        return "{name};{source};{package};{value};{inrange}".format(
            name=value.name,
            source=value.source,
            package=value.package,
            value=value.value,
            inrange=value.in_range
        )

    def _metrics_info_as_line(self) -> str:
        return "{scope};{id};{desc};{max};{min};{hint}".format(
            scope=self.scope,
            id=self.id,
            desc=self.description,
            max=self.max,
            min=self.min,
            hint=self.hint
        )

    def _stats_as_line(self) -> str:
        return "{per};{avg};{stddev};{max};{total};{max_in_range}".format(
            per=self.stats.per,
            avg=self.stats.avg,
            stddev=self.stats.stddev,
            max=self.stats.max,
            total=self.stats.total,
            max_in_range=self.stats.max_in_range
        )


class Metrics3XMLParser:

    @staticmethod
    def get_columns_line() -> str:
        column_titles: List[str] = [
            "scope",
            "metric_id",
            "metric_desc",
            "metric_max",
            "metric_min",
            "metric_hint",

            "values_per",
            "values_avg",
            "values_stddev",
            "values_max",
            "values_total",
            "values_max_in_range",

            "value_name",
            "value_source",
            "value_package",
            "value",
            "value_in_range"
        ]

        return ";".join(column_titles)

    @staticmethod
    def parse(xml_file_path: str) -> List[Metric]:
        xml_content: str

        with open(xml_file_path, "r") as xml:

            xml_content = xml.read()
            xml_content = Metrics3XMLParser.remove_namespace(xml_content)
            xml_content = xml_content.replace(";", "")

        root = Etree.fromstring(xml_content)

        metrics: List[Metric] = list()

        scope: str = root.attrib.get("scope")

        for m in root.iterfind('Metric'):
            metric: Metric = Metric(**m.attrib, scope=scope)

            values: List[Value] = [Value(**v.attrib) for v in m.iterfind('.//Value')]

            values_parent = m.find('.//Values')
            stats: Stats = Stats(**values_parent.attrib) if values_parent else Stats()

            metric.with_values(values)
            metric.with_stats(stats)

            metrics.append(metric)

        return metrics

    @staticmethod
    def remove_namespace(xml_content: str):
        return re.sub(r"xmlns=\".*\"", '', xml_content)


m: List[Metric] = Metrics3XMLParser.parse("xml/xml1.xml")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Path for the csv output', required=True)
    parser.add_argument('-f', '--files', nargs='+', help='List the files you want to parse in the csv output',
                        required=True)

    args = parser.parse_args()

    files: List[str] = args.files
    output_path: str = args.output

    csv_content = Metrics3XMLParser.get_columns_line() + "\n"

    for file in files:
        file_metrics: List[Metric] = Metrics3XMLParser.parse(file)

        for file_metric in file_metrics:
            csv_content += "".join(file_metric.as_csv())

    with open(output_path, "w") as csv_output:
        csv_output.write(csv_content)


if __name__ == '__main__':
    main()
