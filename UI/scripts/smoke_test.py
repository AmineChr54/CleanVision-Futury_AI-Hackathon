import sys
import os
# Ensure project root is on sys.path when running from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import CleanVisionApp

print('Building app and ScreenManager...')
app = CleanVisionApp()
sm = app.build()
print('Screens:', [getattr(s, 'name', repr(s)) for s in sm.screens])

try:
    res = sm.get_screen('results')
except Exception as e:
    print('ERROR: could not get results screen:', e)
    sys.exit(2)

print('Calling display_inspection_results(...)')
res.display_inspection_results('C:/temp/fake_image.jpg')
print('current_image_path:', getattr(res, 'current_image_path', None))
print('last_inspection_result:', getattr(res, 'last_inspection_result', None))

print('Opening rating screen...')
res.open_rating(None)
print('ScreenManager current:', sm.current)

rating = sm.get_screen('rating')
print('rating_image.source:', getattr(rating, 'rating_image', None) and rating.rating_image.source)
print('rating _scores:', getattr(rating, '_scores', None))
print('rating data_label:', getattr(getattr(rating, 'data_label', None), 'text', None))
print('Smoke test completed.')
