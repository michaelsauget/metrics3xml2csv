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
        self.id: str = kwargs.get("id", "")
        self.code: str = kwargs.get("id", "") + "_" + kwargs.get("id_extension", "")
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
        return "{target_name};{target_source};{target_package};{target_value};{target_in_range}".format(
            target_name=value.name,
            target_source=value.source,
            target_package=value.package,
            target_value=value.value,
            target_in_range=value.in_range
        )

    def _metrics_info_as_line(self) -> str:
        return "{scope};{metric_id};{metric_code};{metric_desc};{metric_max};{metric_min};{metric_hint}".format(
            scope=self.scope,
            metric_id=self.id,
            metric_code=self.code,
            metric_desc=self.description,
            metric_max=self.max,
            metric_min=self.min,
            metric_hint=self.hint
        )

    def _stats_as_line(self) -> str:
        return "{stats_per};{stats_avg};{stats_stddev};{stats_max};{stats_total};{stats_max_in_range}".format(
            stats_per=self.stats.per,
            stats_avg=self.stats.avg,
            stats_stddev=self.stats.stddev,
            stats_max=self.stats.max,
            stats_total=self.stats.total,
            stats_max_in_range=self.stats.max_in_range
        )


class Metrics3XMLParser:

    @staticmethod
    def get_columns_line() -> str:
        column_titles: List[str] = [
            "scope",

            "metric_id",
            "metric_code",
            "metric_desc",
            "metric_max",
            "metric_min",
            "metric_hint",

            "stats_per",
            "stats_avg",
            "stats_stddev",
            "stats_max",
            "stats_total",
            "stats_max_in_range",

            "target_name",
            "target_source",
            "target_package",
            "target_value",
            "target_in_range"
        ]

        return ";".join(column_titles)

    @staticmethod
    def parse(xml_file_path: str) -> List[Metric]:
        xml_content: str

        with open(xml_file_path, "r") as xml:

            xml_content = xml.read()
            # for XML understanding
            xml_content = Metrics3XMLParser.remove_namespace(xml_content)
            # for CSV
            xml_content = xml_content.replace(";", "")
            # for xml parsing
            xml_content = xml_content.replace("\&lt", "")
            xml_content = xml_content.replace("&gt", "")

        root = Etree.fromstring(xml_content)

        metrics: List[Metric] = list()

        scope: str = root.attrib.get("scope")

        for m in root.iterfind('Metric'):

            # values_parent = m.iterfind('.//Value/..')

            for values_parent in m.iterfind('.//Value/..'):

                metric: Metric = Metric(scope=scope, **m.attrib, id_extension=values_parent.attrib.get("per", ""))

                stats: Stats = Stats(**values_parent.attrib) if values_parent.tag == "Values" else Stats()

                values: List[Value] = [Value(**v.attrib) for v in values_parent.iterfind('.//Value')]

                metric.with_values(values)
                metric.with_stats(stats)

                metrics.append(metric)

        return metrics

    @staticmethod
    def _extract_values(m):
        ...

    @staticmethod
    def remove_namespace(xml_content: str):
        return re.sub(r"xmlns=\".*\"", '', xml_content)


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
