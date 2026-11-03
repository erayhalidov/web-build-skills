<?php
// Standalone OCMOD refresh for OpenCart 2.3 — replicates admin > Extensions > Modifications > Refresh.
// Rebuilds system/storage/modification/ from system/modification.xml + system/*.ocmod.xml + oc_modification table.
// Run as the site user (or root) after editing/removing system/*.ocmod.xml.
// Usage: php ocmod_refresh.php
// Adjust the constants below to the target store.

error_reporting(E_ALL & ~E_NOTICE & ~E_WARNING);

define('DIR_APPLICATION', '/home/<user>/htdocs/<site>/admin/');
define('DIR_SYSTEM', '/home/<user>/htdocs/<site>/system/');
define('DIR_CATALOG', '/home/<user>/htdocs/<site>/catalog/');
define('DIR_MODIFICATION', '/home/<user>/htdocs/<site>/system/storage/modification/');

$DB_HOST = 'localhost'; $DB_USER = 'user'; $DB_PASS = 'pass'; $DB_NAME = 'db';

$db = new mysqli($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);
$db->set_charset('utf8');
if ($db->connect_error) { die("DB error: " . $db->connect_error . "\n"); }

// ---------- 1. Clear all modification files ----------
$path = array(DIR_MODIFICATION . '*');
$files = array();
while (count($path) != 0) {
    $next = array_shift($path);
    foreach (glob($next) as $file) {
        if (is_dir($file)) { $path[] = $file . '/*'; }
        $files[] = $file;
    }
}
rsort($files);
foreach ($files as $file) {
    if ($file != DIR_MODIFICATION . 'index.html') {
        if (is_file($file)) unlink($file);
        elseif (is_dir($file)) rmdir($file);
    }
}
echo "cleared modification dir\n";

// ---------- 2. Collect XML sources ----------
$xml = array();
$xml[] = file_get_contents(DIR_SYSTEM . 'modification.xml');
$g = glob(DIR_SYSTEM . '*.ocmod.xml');
if ($g) { foreach ($g as $f) { $xml[] = file_get_contents($f); } }
$r = $db->query("SELECT xml FROM oc_modification WHERE status = '1'");
while ($row = $r->fetch_assoc()) { $xml[] = $row['xml']; }
echo "XML sources: " . count($xml) . "\n";

// ---------- 3. Apply modifications ----------
$modification = array();
$original = array();

function applyXml($x, &$modification, &$original) {
    global $db;
    if (empty($x)) return;
    $dom = new DOMDocument('1.0', 'UTF-8');
    $dom->preserveWhiteSpace = false;
    @$dom->loadXml($x);
    $mods = $dom->getElementsByTagName('modification');
    if ($mods->length == 0) return;
    $recovery = $modification;

    $fileEls = $mods->item(0)->getElementsByTagName('file');
    foreach ($fileEls as $fileEl) {
        $operations = $fileEl->getElementsByTagName('operation');
        $pathList = explode('|', $fileEl->getAttribute('path'));
        foreach ($pathList as $fp) {
            $path = '';
            if (substr($fp, 0, 7) == 'catalog') $path = DIR_CATALOG . substr($fp, 8);
            elseif (substr($fp, 0, 5) == 'admin') $path = DIR_APPLICATION . substr($fp, 6);
            elseif (substr($fp, 0, 6) == 'system') $path = DIR_SYSTEM . substr($fp, 7);
            if (!$path) continue;
            $realFiles = glob($path, GLOB_BRACE);
            if (!$realFiles) continue;
            foreach ($realFiles as $realFile) {
                if (substr($realFile, 0, strlen(DIR_CATALOG)) == DIR_CATALOG) $key = 'catalog/' . substr($realFile, strlen(DIR_CATALOG));
                elseif (substr($realFile, 0, strlen(DIR_APPLICATION)) == DIR_APPLICATION) $key = 'admin/' . substr($realFile, strlen(DIR_APPLICATION));
                elseif (substr($realFile, 0, strlen(DIR_SYSTEM)) == DIR_SYSTEM) $key = 'system/' . substr($realFile, strlen(DIR_SYSTEM));
                else continue;

                if (!isset($modification[$key])) {
                    $content = file_get_contents($realFile);
                    $modification[$key] = preg_replace('~\r?\n~', "\n", $content);
                    $original[$key] = $modification[$key];
                }

                foreach ($operations as $operation) {
                    $error = $operation->getAttribute('error');
                    $ignoreif = $operation->getElementsByTagName('ignoreif')->item(0);
                    if ($ignoreif) {
                        if ($ignoreif->getAttribute('regex') != 'true') {
                            if (strpos($modification[$key], $ignoreif->textContent) !== false) continue;
                        } else {
                            if (preg_match($ignoreif->textContent, $modification[$key])) continue;
                        }
                    }
                    $status = false;
                    $searchNode = $operation->getElementsByTagName('search')->item(0);
                    $addNode = $operation->getElementsByTagName('add')->item(0);
                    if (!$searchNode || !$addNode) continue;

                    if ($searchNode->getAttribute('regex') != 'true') {
                        $search = $searchNode->textContent;
                        $trim = $searchNode->getAttribute('trim');
                        $index = $searchNode->getAttribute('index');
                        $add = $addNode->textContent;
                        $addTrim = $addNode->getAttribute('trim');
                        $position = $addNode->getAttribute('position');
                        $offset = $addNode->getAttribute('offset');
                        if ($offset == '') $offset = 0;
                        if (!$trim || $trim == 'true') $search = trim($search);
                        if ($addTrim == 'true') $add = trim($add);
                        $indexes = ($index !== '') ? explode(',', $index) : array();
                        $i = 0;
                        $lines = explode("\n", $modification[$key]);
                        for ($line_id = 0; $line_id < count($lines); $line_id++) {
                            $line = $lines[$line_id];
                            $match = false;
                            if (stripos($line, $search) !== false) {
                                if (!$indexes) $match = true;
                                elseif (in_array($i, $indexes)) $match = true;
                                $i++;
                            }
                            if ($match) {
                                switch ($position) {
                                    default:
                                    case 'replace':
                                        if ($offset < 0) {
                                            array_splice($lines, $line_id + $offset, abs($offset) + 1, array(str_replace($search, $add, $line)));
                                            $line_id -= $offset;
                                        } else {
                                            array_splice($lines, $line_id, $offset + 1, array(str_replace($search, $add, $line)));
                                        }
                                        break;
                                    case 'before':
                                        $new_lines = explode("\n", $add);
                                        array_splice($lines, $line_id - $offset, 0, $new_lines);
                                        $line_id += count($new_lines);
                                        break;
                                    case 'after':
                                        $new_lines = explode("\n", $add);
                                        array_splice($lines, ($line_id + 1) + $offset, 0, $new_lines);
                                        $line_id += count($new_lines);
                                        break;
                                }
                                $status = true;
                            }
                        }
                        $modification[$key] = implode("\n", $lines);
                    } else {
                        $search = trim($searchNode->textContent);
                        $limit = $searchNode->getAttribute('limit');
                        $replace = trim($addNode->textContent);
                        if (!$limit) $limit = -1;
                        $match = array();
                        preg_match_all($search, $modification[$key], $match, PREG_OFFSET_CAPTURE);
                        if ($limit > 0) $match[0] = array_slice($match[0], 0, $limit);
                        if ($match[0]) $status = true;
                        $modification[$key] = preg_replace($search, $replace, $modification[$key], $limit);
                    }

                    if (!$status) {
                        if ($error == 'abort') { $modification = $recovery; return; }
                        elseif ($error == 'skip') continue;
                        else break;
                    }
                }
            }
        }
    }
}

foreach ($xml as $x) { applyXml($x, $modification, $original); }

// ---------- 4. Write changed files ----------
$written = 0;
foreach ($modification as $key => $value) {
    if (!isset($original[$key]) || $original[$key] != $value) {
        $dir = dirname($key);
        $path = '';
        foreach (explode('/', $dir) as $d) {
            $path .= '/' . $d;
            if (!is_dir(DIR_MODIFICATION . $path)) @mkdir(DIR_MODIFICATION . $path, 0777, true);
        }
        file_put_contents(DIR_MODIFICATION . $key, $value);
        $written++;
    }
}
echo "modified files written: $written\n";
$db->close();
echo "DONE\n";
