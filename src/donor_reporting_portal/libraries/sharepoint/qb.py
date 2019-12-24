from office365.sharepoint.helpers.camlquery_builder import CamlQueryBuilder, recursive_builder
from office365.sharepoint.helpers.utils import to_camel


class ICamlQueryBuilder(CamlQueryBuilder):

    def create_query(self):
        where_condition = ''

        if self.filters.keys():
            filter_queries = []
            for filter_name, filter_value in self.filters.items():
                querystring_operator = filter_name.split('__')[-1]
                operator = self.mapping_operator.get(querystring_operator, 'Eq')

                filter_name = to_camel(filter_name.split('__')[0])
                if operator in self.date_operators:
                    column_type, value = 'DateTime', "{}T00:00:00Z".format(filter_value)  # 2016-03-26
                    query = '<{}><FieldRef Name="{}" /><Value Type="{}">{}</Value></{}>'.format(
                        operator, filter_name, column_type, value, operator)
                elif operator == 'Contains':
                    column_type = 'Text'  #'Note'
                    query = '<{}><FieldRef Name="{}" /><Value Type="{}">{}</Value></{}>'.format(
                            operator, filter_name, column_type, filter_value, operator)
                else:
                    column_type, values = 'Text', filter_value.split(',')
                    query = ''
                    for value in values:
                        query = query + '<{}><FieldRef Name="{}" /><Value Type="{}">{}</Value></{}>'.format(
                            operator, filter_name, column_type, value, operator)
                    if len(values) > 1:
                        query = f'<Or>{query}</Or>'
                filter_queries.append(query)
            where_condition = recursive_builder(filter_queries)
            if len(filter_queries) > 1:
                where_condition = f"<And>{where_condition}</And>"

        scope = f' Scope="{self.scope}"' if self.scope else ''
        query = f'<View{scope}><Query><Where>{where_condition}</Where></Query></View>'
        return query
