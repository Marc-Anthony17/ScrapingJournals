# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class JournalsPipeline:
    def process_item(self, item, spider):
       
        adapter = ItemAdapter(item)
        field_names = ['title','authors','publish_date','journal_name','doi','citations']
        for field_name in field_names:
            
            value = adapter.get(field_name)
            adapter[field_name] =value.replace("\n", "").strip()

            if field_name == 'citations':
                adapter[field_name] =value.replace("Citations: ", "").strip()

        return item
