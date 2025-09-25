# Canvas API Scripts

This repo contains scripts for using the Canvas API.

## Extracting Peer Reviews

Use the script `get_peer_reviews.py` to extract data for peer reviews.

For example:
```
time python get_peer_reviews.py -c 28425 -a 646781 -r 9735 -ra 21957 -at <your-access-token-here>
```

To get your access token, go to your profile on Canvas and generate one.

To get the course id, click on the course and see the id in the URL. e.g.: `https://canvas.ualberta.ca/courses/28425`

To get the assignment id, click on the assignment in the course and see the assignment id in the url. e.g.: `https://canvas.ualberta.ca/courses/28425/assignments/646781`

To get the rubrics id and rubrics association id, hover over the edit button on the rubric on the assignment (don't click). Both ids will appear in the link preview at the bottom left of the browser (assuming your browser has that feature). e.g.: `https://canvas.ualberta.ca/courses/28425/rubrics/9735?rubrics_association_id=21957`
