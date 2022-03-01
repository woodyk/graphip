#!/Users/flint/opt/anaconda3/bin/python3
#
# graph.py -- Wadih Khairallah <woody@smallroom.com>
# https://neo4j.com/docs/api/python-driver/4.4/

import logging
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

class Graph:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_relation(self, ipsrc, ipdst):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_relation, ipsrc, ipdst)
            for record in result:
                print("Created relation between: {ips}, {ipd}".format(
                    ips=record['ips'], ipd=record['ipd']))

    @staticmethod
    def _create_and_return_relation(tx, ipsrc, ipdst):

        # To learn more about the Cypher syntax,
        # see https://neo4j.com/docs/cypher-manual/current/

        # The Reference Card is also a good resource for keywords,
        # see https://neo4j.com/docs/cypher-refcard/current/

        query = (
            "MERGE (ips:IP { value: $ipsrc }) "
            "MERGE (ipd:IP { value: $ipdst }) "
            "MERGE (ips)-[:TALKS_TO]->(ipd) "
            "RETURN ips, ipd"
        )

        result = tx.run(query, ipsrc=ipsrc, ipdst=ipdst)
        try:
            return [{"ips": record["ips"]["value"], "ipd": record["ipd"]["value"]}
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

'''
if __name__ == "__main__":
    # See https://neo4j.com/developer/aura-connect-driver/ for Aura specific connection URL.
    scheme = "neo4j"  # Connecting to Aura, use the "neo4j+s" URI scheme
    host_name = "localhost"
    port = 7687
    url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
    user = "neo4j"
    password = '12#9akk' 
    graph = Graph(url, user, password)
    graph.create_relation(ipsrc, ipdst)
    graph.close()
'''
